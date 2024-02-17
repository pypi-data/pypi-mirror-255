from typing import Optional
from ytvs.client.official.api import OfficialApi
from ytvs.client.unofficial.api import UnofficialApi
from ytvs.filter import SearchType, Order, VideoDuration
from ytvs.models import CommentThreadListResponse, SearchListResponse, ChannelListResponse, VideoListResponse, \
    CommentListResponse, CaptionListResponse
from ytvs.models.transcript import TranscriptSnippet


class YoutubeApi(object):
    """
       YouTubeApi 클래스는 YouTube의 공식 및 비공식 API에 대한 접근을 제공.
       이 클래스는 다양한 YouTube 리소스에 대한 검색, 비디오 정보 조회, 채널 정보 조회, 댓글 스레드 조회 등의 기능을 제공.
       사용자는 공식 API와 비공식 API 중 하나를 선택하여 사용 가능.
   """

    def __init__(self,
                 *,
                 api_key: str):
        """
        YouTube API 클래스의 생성자. 공식 및 비공식 API 클라이언트를 초기화.
        :param api_key: YouTube API를 사용하기 위한 API 키.
        """
        self._official_client = OfficialApi(api_key=api_key)
        self._unofficial_client = UnofficialApi()
        self._use_official = False

    def search(self,
               *,
               q: str,
               search_type: SearchType,
               order: Order,
               video_duration: VideoDuration,
               limit=10,
               page_token: Optional[str] = None,
               use_official: Optional[bool] = False
               ) -> SearchListResponse:
        """
        YouTube에서 키워드를 이용해 검색.
        지원:공식API   -    O
            비공식API  -    O
        :param q: 검색어.
        :param search_type: 검색 유형.
        :param order: 검색 결과의 정렬 순서.
        :param video_duration: 검색할 비디오의 길이.
        :param limit: 검색 결과의 최대 개수.
        :param page_token: 페이징을 위한 토큰입
        :param use_official: 공식 API를 사용할지 여부.
        :return: 검색 결과.
        """
        if use_official:
            # 공식 API를 사용하여 채널 정보를 가져옵니다.
            return self._official_client.search_by_keywords(
                q=q,
                search_type=search_type,
                order=order,
                video_duration=video_duration,
                limit=limit,
                page_token=page_token
            )
        else:
            # 비공식 API를 사용하여 채널 정보를 가져옵니다.
            result_dict = self._unofficial_client.search.search(
                q,
                search_type,
                order,
                video_duration,
                limit,
                page_token
            )
            return SearchListResponse.from_dict(result_dict)

    def get_channel_info(self,
                         *,
                         channel_id: str,
                         use_official: Optional[bool] = False
                         ) -> ChannelListResponse:
        """
        지정된 YouTube 채널의 정보를 조회. 공식 API와 비공식 API를 선택적으로 사용 가능.
        :param channel_id: 정보를 가져올 채널의 ID.
        :param use_official: 공식 API를 사용할지 여부. 기본값은 False.
        :return: 채널 정보를 포함한 ChannelListResponse 객체.
        """
        if use_official:
            # 공식 API를 사용하여 채널 정보를 가져옵니다.
            return self._official_client.get_channel_info(channel_id=channel_id)
        else:
            # 비공식 API를 사용하여 채널 정보를 가져옵니다.
            result_dict = self._unofficial_client.channel.get_channel_info(channel_id=channel_id)
            return ChannelListResponse.from_dict(result_dict)

    def get_video_by_id(self,
                        *,
                        video_id,
                        use_official=False) -> VideoListResponse:
        """
        YouTube 채널 정보를 획득.
        지원:공식API    -    O
            비공식API   -    O
        :param channel_id: 정보를 가져올 채널의 ID.
        :param use_official: 공식 API를 사용할지 여부.
        :return: 채널 정보입니다.
        """
        if use_official:
            # 공식 API를 사용하여 채널 정보를 가져옵니다.
            return self._official_client.get_video_by_id(video_id=video_id)
        else:
            # 비공식 API를 사용하여 채널 정보를 가져옵니다.
            data = self._unofficial_client.video.get_video_by_id(video_id=video_id)
            return VideoListResponse.from_dict(data)

    def get_comment_threads(self,
                            *,
                            video_id,
                            use_official=False) -> CommentThreadListResponse:
        """
        YouTube 비디오의 댓글 스레드를 조회.
        지원:공식API   -    O
            비공식API  -    O
        :param video_id: 댓글 스레드를 가져올 비디오의 ID입니다.
        :param use_official: 공식 API를 사용할지 여부입니다.
        :return: 댓글 스레드 정보입니다.
        """
        if use_official:
            # 공식 API를 사용하여 채널 정보를 가져옵니다.
            return self._official_client.get_comment_threads(video_id=video_id)
        else:
            # 비공식 API를 사용하여 채널 정보를 가져옵니다.
            data = self._unofficial_client.comment_thread.get_comment_threads(video_id=video_id)
            return CommentThreadListResponse.from_dict(data)

    def get_comments_official(self,
                              *,
                              parent_id: str,
                              page_token: str) -> CommentListResponse:
        """

        지원:
            공식API   -    O
            비공식API -    O
        :return:
        """
        # 공식 API를 사용하여 채널 정보를 가져옵니다.
        return self._official_client.get_comments(parent_id=parent_id, page_token=page_token)

    def get_comments_unofficial(self,
                                *,
                                page_token: str) -> CommentListResponse:
        """

        지원:
            공식API   -    O
            비공식API -    O
        :return:
        """
        # 비공식 API를 사용하여 채널 정보를 가져옵니다.
        data = self._unofficial_client.comment.get_comments(page_token=page_token)
        return CommentListResponse.from_dict(data)

    def get_transcript_by_video_id(self,
                                   *
                                   video_id: str,
                                   use_official: bool = False
                                   ) -> TranscriptSnippet:
        """
        YouTube 비디오의 자막 정보를 조회.
        지원:공식API   -    X
            비공식API  -    O
        :param video_id: 자막 정보를 가져올 비디오의 ID입니다.
        :param use_official: 공식 API를 사용할지 여부입니다.
        :return: 자막 정보입니다. 공식 API에서는 지원되지 않습니다.
        """
        if use_official:
            # 공식 API는 지원하지 않음.
            raise NotImplemented("Not supported in official api")
        else:
            # 비공식 API를 사용하여 채널 정보를 가져옵니다.
            data = self._unofficial_client.transcript.get_transcript_by_video_id(video_id=video_id)
            return TranscriptSnippet.from_dict(data)

    def get_caption_by_video_id(self,
                                *
                                video_id: str,
                                use_official: bool = False
                                ) -> CaptionListResponse:
        """
        YouTube 비디오의 캡션 정보를 조회.
        지원:공식API   -    O
            비공식API  -    X
        :param video_id: 캡션 정보를 가져올 비디오의 ID.
        :param use_official: 공식 API를 사용할지 여부.
        :return: 캡션 정보입니다. 비공식 API는 미지원.
        """
        if use_official:
            # 공식 API를 사용하여 채널 정보를 가져옵니다.
            return self._official_client.get_captions_by_video(video_id=video_id)
        else:
            # 비공식 API는 지원하지 않음.
            raise NotImplemented("Not supported in unofficial api")
