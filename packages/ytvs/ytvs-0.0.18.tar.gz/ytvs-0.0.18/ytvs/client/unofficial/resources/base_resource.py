from typing import Optional, TYPE_CHECKING
# TYPE_CHECKING: 런타임 시에는 무시되고, 타입 체크 도구에서만 사용
if TYPE_CHECKING:
    # 비공식 YouTube 클라이언트를 임포트합니다. 이는 타입 체킹을 위해서만 사용
    from ytvs.client.unofficial.client import UnofficialClient


class Resource:
    """ Resource base class
    YouTube 비공식 API에 접근하기 위한 기본 자원 클래스
    """

    # YouTube 데스크톱 및 모바일 버전의 기본 URL
    DESKTOP_URL = f'https://www.youtube.com/'
    MOBILE_URL = f'https://www.youtube.com/'

    # YouTube API의 특정 기능에 접근하기 위한 URL들
    SEARCH_V1_URL = 'https://m.youtube.com/youtubei/v1/search'
    CONTINUATION_URL = 'https://m.youtube.com/youtubei/v1/next'
    TRANSCRIPT_API = 'https://m.youtube.com/youtubei/v1/get_transcript'

    # YouTube API에 접근하기 위한 키
    API_KEY = 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'

    # YouTube API 요청 시 사용되는 클라이언트 정보
    CONTEXT_PARAM = {
        'context': {
            'client': {
                'hl': 'ko',  # en
                'gl': 'KR',  # US
                'clientName': 'WEB',  # MWEB
                'clientVersion': '2.20210804.02.00',
            },
        }
    }

    def __init__(self, client: Optional["UnofficialClient"] = None):
        """
        # Resource 클래스의 생성자입니다. 비공식 클라이언트 인스턴스를 선택적으로 받습니다.
        :param client:
        """
        self._client = client

    def build_video_resource_url(self, video_id:str):
        """
        YouTube 비디오의 URL을 생성합니다.
        :param video_id: 생성할 URL의 비디오 ID입니다.
        :return: YouTube 비디오의 전체 URL을 반환합니다.
        """
        return f'{self.DESKTOP_URL}/watch?v={video_id}'

    def build_transcript_resource_url(self):
        """
        YouTube 동영상의 자막 정보에 접근하기 위한 API URL을 생성합니다.
        :return: 자막 정보에 접근하기 위한 API URL을 반환합니다.
        """
        return f'{self.TRANSCRIPT_API}?key={self.API_KEY}'

    def build_channel_resource_url(self, channel_id:str):
        """
        특정 YouTube 채널의 URL을 생성합니다.
        :param channel_id: 생성할 URL의 채널 ID입니다.
        :return: YouTube 채널의 전체 URL을 반환합니다.
        """
        return f'{self.DESKTOP_URL}channel/{channel_id}'

    def build_continuous_resource_url(self):
        """
        YouTube API에서 연속된 데이터에 접근하기 위한 URL을 생성합니다.
        :return: 연속된 데이터에 접근하기 위한 API URL을 반환합니다.
        """
        return f'{self.CONTINUATION_URL}/?key={self.API_KEY}'

    def build_search_resource_url(self, keyword_query, filter_query):
        """
        YouTube 검색 결과에 접근하기 위한 URL을 생성합니다.
        :param keyword_query: 검색어입니다.
        :param filter_query: 검색 결과를 필터링하는 쿼리입니다.
        :return: 검색 결과에 접근하기 위한 URL을 반환합니다.
        """
        return f'{self.DESKTOP_URL}/results?search_query={keyword_query}&sp={filter_query}'

    def build_search_v1_resource_url(self):
        """
        YouTube의 새로운 검색 API에 접근하기 위한 URL을 생성합니다.
        :param c_token: 검색 API에 접근하기 위한 토큰입니다.
        :return: 검색 API에 접근하기 위한 URL을 반환합니다.
        """
        return f'{self.SEARCH_V1_URL}?key={self.API_KEY}'
