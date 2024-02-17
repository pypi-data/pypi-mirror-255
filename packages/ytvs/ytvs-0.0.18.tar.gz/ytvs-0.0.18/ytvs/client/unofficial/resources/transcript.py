import json
import dpath
from ytvs.constants import CONTENT_TYPE_JSON_HEADER, MOBILE_XHR_HEADERS
from ytvs.extractor import YoutubeBasicInfoExtractor
from .base_resource import Resource
from ytvs.utils import try_get, _search_attribute
from ..parameter import DataParameterBuilder


def _parse_transcript_data(raw_data):
    """
    YouTube 동영상 자막(raw_data)을 파싱.
    :param raw_data: 파싱할 자막 데이터.
    :return: 파싱된 자막 데이터.
    """
    transcrtipt_segment_list_renderer = _search_attribute(raw_data, 'transcriptSegmentListRenderer', 20)
    transcripts = YoutubeBasicInfoExtractor.extract_transcript_segment_list_renderer(transcrtipt_segment_list_renderer)
    transcript_count = len(transcripts)

    return {
        'kind': 'youtube#TranscriptResponse',
        'etag': None,
        'items': transcripts,
        'nextPageToken': None,
        'pageInfo': {
            'resultsPerPage': transcript_count,
            'totalResults': transcript_count
        },
        'prevPageToken': None
    }


class TranscriptResource(Resource):
    def get_transcript_by_video_id(self, video_id):
        """
        주어진 비디오 ID에 대한 자막을 조회.
        :param video_id: 자막을 요청할 비디오의 ID.
        :return: 파싱된 자막 데이터.
        """
        # 1. 영상 정보로부터 Transcript를 획득할 수 있는 Token을 획득
        transcript_token = self._request_video_transcript_token(video_id)

        # 2. transcript raw 데이터 획득
        transcript_contents_raw = self._request_video_transcript_contents(transcript_token)

        # 3. raw 데이터에서 필요한 데이터만 파싱
        return _parse_transcript_data(transcript_contents_raw)

    def _request_video_transcript_token(self, video_id: str):
        """
        주어진 비디오 ID에 대한 자막 토큰을 요청.
        :param video_id: 자막 토큰을 요청할 비디오의 ID.
        :return: 자막 토큰.
        """
        # 1. 연결 URL 생성
        endpoint = self.build_video_resource_url(video_id)
        video_html_text = self._client.fetch_url(endpoint).decode('utf-8')

        # 2. 데이터 파싱
        yt_initial_data = YoutubeBasicInfoExtractor.extract_yt_initial_data(video_html_text)
        transcript_token = dpath.get(
            yt_initial_data['init_data'],
            "**/content/continuationItemRenderer/continuationEndpoint/getTranscriptEndpoint/params",
            default=None,
        )
        return transcript_token

    def _request_video_transcript_contents(self, transcript_token):
        """
        주어진 토큰을 사용하여 YouTube 동영상의 자막 내용을 요청.
        :param transcript_token: 자막을 요청할 토큰.
        :return: 자막 내용의 Raw 데이터.
        """
        request_url = self.build_transcript_resource_url()
        data = json.dumps(DataParameterBuilder().set_param(transcript_token).build())
        content_bytes = self._client.fetch_url(
            request_url, headers=MOBILE_XHR_HEADERS + CONTENT_TYPE_JSON_HEADER, data=data)
        content_text = content_bytes.decode('utf-8')
        content_dict = json.loads(content_text)
        return content_dict
