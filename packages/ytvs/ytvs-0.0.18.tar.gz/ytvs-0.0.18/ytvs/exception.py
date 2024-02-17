import urllib.parse
from typing import Optional, Union
from requests import Response
from ytvs.error import ErrorMessage


class HTTPAsymmetricCookieProcessor(urllib.request.BaseHandler):
    '''Separate cookiejars for receiving and sending'''

    def __init__(self, cookiejar_send=None, cookiejar_receive=None):
        import http.cookiejar
        self.cookiejar_send = cookiejar_send
        self.cookiejar_receive = cookiejar_receive

    def http_request(self, request):
        if self.cookiejar_send is not None:
            self.cookiejar_send.add_cookie_header(request)
        return request

    def http_response(self, request, response):
        if self.cookiejar_receive is not None:
            self.cookiejar_receive.extract_cookies(response, request)
        return response

    https_request = http_request
    https_response = http_response


class FetchError(Exception):
    def __init__(self, code, reason='', ip=None, error_message=None):
        if error_message:
            string = code + ' ' + reason + ': ' + error_message
        else:
            string = 'HTTP error during request: ' + code + ' ' + reason
        Exception.__init__(self, string)
        self.code = code
        self.reason = reason
        self.ip = ip
        self.error_message = error_message


class PyYouTubeException(Exception):
    """
    This is a return demo:
    {'error': {'errors': [{'domain': 'youtube.parameter',
    'reason': 'missingRequiredParameter',
    'message': 'No filter selected. Expected one of: forUsername, managedByMe, categoryId, mine, mySubscribers, id, idParam',
    'locationType': 'parameter',
    'location': ''}],
    'code': 400,
    'message': 'No filter selected. Expected one of: forUsername, managedByMe, categoryId, mine, mySubscribers, id, idParam'}}
    """

    def __init__(self, response: Optional[Union[ErrorMessage, Response]]):
        self.status_code: Optional[int] = None
        self.error_type: Optional[str] = None
        self.message: Optional[str] = None
        self.response: Optional[Union[ErrorMessage, Response]] = response
        self.error_handler()

    def error_handler(self):
        """
        Error has two big type(but not the error type.): This module's error, Api return error.
        So This will change two error to one format
        """
        if isinstance(self.response, ErrorMessage):
            self.status_code = self.response.status_code
            self.message = self.response.message
            self.error_type = "PyYouTubeException"
        elif isinstance(self.response, Response):
            res_data = self.response.json()
            if "error" in res_data:
                error = res_data["error"]
                if isinstance(error, dict):
                    self.status_code = res_data["error"]["code"]
                    self.message = res_data["error"]["message"]
                else:
                    self.status_code = self.response.status_code
                    self.message = error
                self.error_type = "YouTubeException"

    def __repr__(self):
        return (
            f"{self.error_type}(status_code={self.status_code},message={self.message})"
        )

    def __str__(self):
        return self.__repr__()
