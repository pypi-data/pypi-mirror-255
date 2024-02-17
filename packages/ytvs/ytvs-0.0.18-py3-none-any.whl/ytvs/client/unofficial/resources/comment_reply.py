import base64
import json

from ytvs import proto
from ytvs.client.unofficial.parameter import DataParameterBuilder
from ytvs.client.unofficial.resources.base_resource import Resource
from ytvs.constants import MOBILE_XHR_HEADERS, CONTENT_TYPE_JSON_HEADER
from ytvs.extractor import YoutubeBasicInfoExtractor
from ytvs.utils import _search_attribute, _search_attributes, try_get, convert_relative_to_absolute_date


class CommentResource(Resource):
    KIND = 'youtube#commentListResponse',  # 댓글 스레드 응답 유형

    # def get_comments(self, video_id, page_token):
    def get_comments(self, page_token):
        # Unofficial 방법으로는 미지원

        comment_raw = self._request_data(page_token=page_token)

        # 2. 획득한 댓글 Raw 데이터에서 필요한 정보만 파싱
        comment = self._parse_comment_data(comment_raw)

        # 4. 반환
        return comment

    def _request_data(self, page_token):
        """
        YouTube API를 통해 댓글 데이터를 요청하는 함수.
        :param video_id: 댓글을 요청할 비디오의 ID.
        :param sort: 댓글 정렬 방식.
        :param offset: 댓글 페이지의 오프셋.
        :param lc: 로케일 설정.
        :param secret_key: 보안 키.
        :param page_token: 페이지 토큰.
        :return: YouTube API로부터 받은 Raw 댓글 데이터.
        """
        c_token = page_token
        endpoint = self.build_continuous_resource_url()
        data = json.dumps(DataParameterBuilder().set_continuation(c_token).build())

        content = self._client.fetch_url(
            endpoint, headers=MOBILE_XHR_HEADERS + CONTENT_TYPE_JSON_HEADER, data=data)
        content = content.decode('utf-8')

        raw_json = json.loads(content)
        return raw_json

    def _parse_comment_data(self, raw_data):
        """
         YouTube API로부터 받은 Raw 댓글 데이터를 파싱하는 함수.
         :param raw_data: YouTube API로부터 받은 Raw 댓글 데이터.
         :return: 파싱된 댓글 데이터.
         """
        # 댓글 본문 정보 획득
        comments = []
        comment_renderers = _search_attributes(raw_data, 'commentRenderer')
        if isinstance(comment_renderers, dict):
            comment_renderers = [comment_renderers]

        if comment_renderers is None:
            total_comment = 0
            continuation_token = None
        else:
            total_comment = len(comment_renderers)

            for comment_renderer in comment_renderers:
                comment = YoutubeBasicInfoExtractor.extract_comment_renderer(comment_renderer)
                comments.append(comment)

            # 댓글 페이징 정보 획득
            comment_continuation_renderer = _search_attributes(raw_data, 'continuationItemRenderer')
            if comment_continuation_renderer is not None:
                comment_continuation = YoutubeBasicInfoExtractor.extract_continuation_item_renderer(
                    comment_continuation_renderer['continuationEndpoint'])
                continuation_token = try_get(comment_continuation, lambda x: x['continuation_command']['token'], str)
            else:
                continuation_token = None

        return {
            'kind': self.KIND,
            'etag': None,
            'items': comments,
            'nextPageToken': continuation_token,
            'pageInfo': {
                'resultsPerPage': 20,
                'totalResults': total_comment,
            },
            'prevPageToken': None
        }
