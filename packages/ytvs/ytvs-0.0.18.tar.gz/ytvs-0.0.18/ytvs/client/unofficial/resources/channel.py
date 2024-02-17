import requests
from typing import Union, Optional

from ytvs.client.unofficial.resources.base_resource import Resource
from ytvs.extractor import YoutubeBasicInfoExtractor
from ytvs.utils import try_get, str_to_int, number_str_abbr_to_int, is_korean_number


class ChannelResource(Resource):
    """
    YouTube 채널과 관련된 정보를 제공하는 클래스.
    이 클래스는 Resource 클래스를 상속받아 YouTube 채널 데이터에 접근하고 파싱하는 기능을 제공.
    """
    KIND = 'youtube#channel'   # YouTube 채널의 종류를 나타내는 상수
    RESOURCE = 'channel'   # 자원의 이름을 나타내는 상수

    def get_channel_info(self,
                         channel_id: Optional[str] = None,
                         parts: Optional[str] = None):
        """
        YouTube 채널의 정보를 가져오는 함수
        :param channel_id: 정보를 가져올 채널 ID.
        :param parts: 요청할 데이터의 특정 부분을 나타내는 매개변수입니다.
        :return: 파싱된 채널 데이터를 반환합니다.
        """
        # 1. 영상 페이지 요청
        data = self._request_data(channel_id)

        # 2. 영상 페이지에서 데이터 추출
        yt_initial_data = YoutubeBasicInfoExtractor.extract_yt_initial_data(data)

        # 3. 데이터 분석 및 파싱
        parsed_data = self._parse_channel_data_from_initial_data(yt_initial_data)
        return parsed_data

    def _request_data(self,
                      channel_id: str):
        """
        YouTube 채널 페이지의 HTML 데이터를 요청하는 함수ㅌ.
        :param channel_id: 요청할 채널의 ID.
        :return: 채널 페이지의 HTML 텍스트를 반환.
        """
        # 1. Channel resource 요청 URL 생성
        endpoint = self.build_channel_resource_url(channel_id)

        # 2. Channel 페이지 요청
        html_text = self._client.fetch_url(endpoint) \
            .decode('utf-8')
        
        # 3. Channel 페이지 html 반환
        return html_text

    def _parse_channel_data_from_initial_data(self, initial_data):
        """
        초기 데이터에서 YouTube 채널 데이터를 파싱하는 함수.
        :param initial_data: YouTube 채널 페이지에서 추출된 초기 데이터.
        :return: 파싱된 채널 데이터를 반환.
       :return:
        """
        # 1. 데이터 분석 및 파싱
        header_raw = try_get(initial_data, lambda x: x['init_data']['header']['c4TabbedHeaderRenderer'])
        header = YoutubeBasicInfoExtractor.extract_channel_header(header_raw)
        metadata_raw = try_get(initial_data, lambda x: x['init_data']['metadata']['channelMetadataRenderer'])
        metadata = YoutubeBasicInfoExtractor.extract_metadata(metadata_raw)
        topbar_raw = try_get(initial_data, lambda x: x['init_data']['topbar']['desktopTopbarRenderer'])
        topbar = YoutubeBasicInfoExtractor.extract_channel_topbar(topbar_raw)

        return {
            'etag': None,
            'kind': 'youtube#channelListResponse',
            'items': [{
                'id': header['channel_id'],
                'kind': self.KIND,
                'localizations': None,
                'etag': None,
                'snippet': {
                    'title': metadata['title'],
                    'description': metadata['description'],
                    'country': topbar['country_code'],
                    'customUrl': header['channel_handle_text'],
                    'publishedAt': None,
                    'thumbnails': header['banner_urls'],
                },
                'statistics': {
                    'subscriberCount': header['subscriber_count'],
                    'videoCount': header['video_count'],
                    'viewCount': None,
                }
            }],
            'nextPageToken': None,
            'prevPageToken': None,
            'pageInfo': {
                'totalResults': 1,
                'resultsPerPage': 5
            }
        }
