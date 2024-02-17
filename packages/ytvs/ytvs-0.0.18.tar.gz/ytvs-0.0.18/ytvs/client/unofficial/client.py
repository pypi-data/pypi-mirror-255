import requests
import socks, sockshandler
import gzip

from ytvs.exception import HTTPAsymmetricCookieProcessor, FetchError

try:
    import brotli
    have_brotli = True
except ImportError:
    have_brotli = False
import urllib.parse
import re
import time
import os
import json
import collections
import traceback
import urllib3
from ytvs.constants import DEFAULT_API_KEY

try:
    import brotli
    have_brotli = True
except ImportError:
    have_brotli = False


class UnofficialClient:


    def __init__(self,
                 api_key=DEFAULT_API_KEY):
        self._api_key = api_key
        self._session = requests.Session()
        self._connection_pool = urllib3.PoolManager(cert_reqs='CERT_REQUIRED')

    def get_pool(self, use_tor):
        return self._connection_pool
        # if not use_tor:
        #     return connection_pool
        # return tor_manager.get_tor_connection_pool()

    def decode_content(self, content, encoding_header):
        encodings = encoding_header.replace(' ', '').split(',')
        for encoding in reversed(encodings):
            if encoding == 'identity':
                continue
            if encoding == 'br':
                content = brotli.decompress(content)
            elif encoding == 'gzip':
                content = gzip.decompress(content)
        return content

    def fetch_url_response(self,
                           url,
                           headers=(),
                           timeout=15,
                           data=None,
                           cookiejar_send=None,
                           cookiejar_receive=None,
                           use_tor=True,
                           max_redirects=None):
        '''
        returns response, cleanup_function
        When cookiejar_send is set to a CookieJar object,
         those cookies will be sent in the request (but cookies in response will not be merged into it)
        When cookiejar_receive is set to a CookieJar object,
         cookies received in the response will be merged into the object (nothing will be sent from it)
        When both are set to the same object, cookies will be sent from the object,
         and response cookies will be merged into it.
        '''
        headers = dict(headers)  # Note: Calling dict() on a dict will make a copy
        if have_brotli:
            headers['Accept-Encoding'] = 'gzip, br'
        else:
            headers['Accept-Encoding'] = 'gzip'

        # prevent python version being leaked by urllib if User-Agent isn't provided
        #  (urllib will use ex. Python-urllib/3.6 otherwise)
        if 'User-Agent' not in headers and 'user-agent' not in headers and 'User-agent' not in headers:
            headers['User-Agent'] = 'Python-urllib'

        method = "GET"
        if data is not None:
            method = "POST"
            if isinstance(data, str):
                data = data.encode('utf-8')
            elif not isinstance(data, bytes):
                data = urllib.parse.urlencode(data).encode('utf-8')

        if cookiejar_send is not None or cookiejar_receive is not None:  # Use urllib
            req = urllib.request.Request(url, data=data, headers=headers)

            cookie_processor = HTTPAsymmetricCookieProcessor(cookiejar_send=cookiejar_send,
                                                             cookiejar_receive=cookiejar_receive)

            # if use_tor and settings.route_tor:
            #     opener = urllib.request.build_opener(sockshandler.SocksiPyHandler(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", settings.tor_port), cookie_processor)
            # else:
            #     opener = urllib.request.build_opener(cookie_processor)
            opener = urllib.request.build_opener(cookie_processor)

            response = opener.open(req, timeout=timeout)
            cleanup_func = (lambda r: None)

        else:
            # Use a urllib3 pool. Cookies can't be used since urllib3 doesn't have easy support for them.
            # default: Retry.DEFAULT = Retry(3)
            # (in connectionpool.py in urllib3)
            # According to the documentation for urlopen, a redirect counts as a
            # retry. So there are 3 redirects max by default.
            if max_redirects:
                retries = urllib3.Retry(3 + max_redirects, redirect=max_redirects, raise_on_redirect=False)
            else:
                retries = urllib3.Retry(3, raise_on_redirect=False)
            # pool = get_pool(use_tor and settings.route_tor)
            pool = self.get_pool(False)
            try:
                response = pool.request(method, url, headers=headers, body=data,
                                        timeout=timeout, preload_content=False,
                                        decode_content=False, retries=retries)
                response.retries = retries
            except urllib3.exceptions.MaxRetryError as e:
                exception_cause = e.__context__.__context__
                # if (isinstance(exception_cause, socks.ProxyConnectionError)
                #         and settings.route_tor):
                if (isinstance(exception_cause, socks.ProxyConnectionError)
                        and False):
                    msg = ('Failed to connect to Tor. Check that Tor is open and '
                           'that your internet connection is working.\n\n'
                           + str(e))
                    raise FetchError('502', reason='Bad Gateway',
                                     error_message=msg)
                elif isinstance(e.__context__,
                                urllib3.exceptions.NewConnectionError):
                    msg = 'Failed to establish a connection.\n\n' + str(e)
                    raise FetchError(
                        '502', reason='Bad Gateway',
                        error_message=msg)
                else:
                    raise
            cleanup_func = (lambda r: r.release_conn())

        return response, cleanup_func

    def fetch_url(self,
                  url,
                  headers=(),
                  timeout=15,
                  report_text=None,
                  data=None,
                  cookiejar_send=None,
                  cookiejar_receive=None,
                  use_tor=True,
                  debug_name=None):
        while True:
            start_time = time.monotonic()

            # response, cleanup_func = fetch_url_response(
            #     url, headers, timeout=timeout, data=data,
            #     cookiejar_send=cookiejar_send, cookiejar_receive=cookiejar_receive,
            #     use_tor=use_tor)
            response, cleanup_func = self.fetch_url_response(
                url, headers, timeout=timeout, data=data,
                cookiejar_send=cookiejar_send, cookiejar_receive=cookiejar_receive,
                use_tor=False)
            response_time = time.monotonic()

            content = response.read()

            read_finish = time.monotonic()

            cleanup_func(response)  # release_connection for urllib3
            content = self.decode_content(content, response.getheader('Content-Encoding', default='identity'))

            # if (settings.debugging_save_responses
            #     and debug_name is not None
            #     and content):
            # save_dir = os.path.join(settings.data_dir, 'debug')
            # if not os.path.exists(save_dir):
            #     os.makedirs(save_dir)
            #
            # with open(os.path.join(save_dir, debug_name), 'wb') as f:
            #     f.write(content)

            # if response.status == 429 or (
            #     response.status == 302 and (response.getheader('Location') == url
            #         or response.getheader('Location').startswith(
            #                'https://www.google.com/sorry/index'
            #            )
            #     )
            # ):
            #     print(response.status, response.reason, response.getheaders())
            #     ip = re.search(
            #         br'IP address: ((?:[\da-f]*:)+[\da-f]+|(?:\d+\.)+\d+)',
            #         content)
            #     ip = ip.group(1).decode('ascii') if ip else None
            #     if not ip:
            #         ip = re.search(r'IP=((?:\d+\.)+\d+)',
            #                        response.getheader('Set-Cookie') or '')
            #         ip = ip.group(1) if ip else None
            #
            #     # don't get new identity if we're not using Tor
            #     if not use_tor:
            #         raise FetchError('429', reason=response.reason, ip=ip)
            #
            #     print('Error: Youtube blocked the request because the Tor exit node is overutilized. Exit node IP address: %s' % ip)
            #
            #     # get new identity
            #     error = tor_manager.new_identity(start_time)
            #     if error:
            #         raise FetchError(
            #             '429', reason=response.reason, ip=ip,
            #             error_message='Automatic circuit change: ' + error)
            #     else:
            #         continue # retry now that we have new identity
            #
            # elif response.status >= 400:
            #     raise FetchError(str(response.status), reason=response.reason,
            #                      ip=None)
            break
        if report_text:
            print(report_text, '    Latency:', round(response_time - start_time, 3), '    Read time:',
                  round(read_finish - response_time, 3))
        return content


    def build_continuation_url_and_data(self,
                               url,
                               api_key,
                               continuation_token):
        c_token = continuation_token
        # Caption
        request_url = f'{url}?key={api_key}'
        data = json.dumps({
            'context': {
                'client': {
                    'hl': 'ko',  # en
                    'gl': 'KR',  # US
                    'clientName': 'WEB',  # MWEB
                    'clientVersion': '2.20210804.02.00',
                },
            },
            'params': c_token.replace('=', '%3D'),
        })

        return {'url':url, 'data':data}
