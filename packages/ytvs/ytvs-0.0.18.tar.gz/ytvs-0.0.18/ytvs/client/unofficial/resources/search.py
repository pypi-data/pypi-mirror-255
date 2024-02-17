import json
import requests

from ytvs.client.unofficial.parameter import DataParameterBuilder
from ytvs.client.unofficial.resources.base_resource import Resource
from ytvs.extractor import YoutubeBasicInfoExtractor
from ytvs.filter import SearchType, Order, VideoDuration, FilterBuilder
from ytvs.utils import _search_attribute, _search_attributes, try_get


class SearchResource(Resource):
    KIND = 'youtube#searchListResponse'   # 검색 결과 응답 유형
    REGION_CODE = 'KR'

    def search(self,
               q: str,
               search_type: SearchType,
               order: Order,
               video_duration: VideoDuration,
               limit=10,
               page_token=None
               ):
        """
        YouTube에서 비디오, 채널, 재생목록을 검색
        :param q: 검색어입니다.
        :param search_type: 검색 유형 (예: 비디오, 채널, 재생목록).
        :param order: 검색 결과의 정렬 순서.
        :param video_duration: 검색할 비디오의 길이.
        :param limit: 검색 결과의 최대 개수.
        :param page_token: 페이징을 위한 토큰.
        :return: 파싱된 검색 결과 데이터.
        """
        # 1. Youtube 검색 데이터 요청
        searched_data = self._request_search(q, search_type, order, video_duration, limit, page_token)
        # 2. 데이터 분석 및 파싱
        parsed_data = self._parse_data(searched_data)
        # 3. 반환
        return parsed_data

    def _request_search(self,
                        q: str,
                        search_type: SearchType,
                        order: Order,
                        video_duration: VideoDuration,
                        limit=10,
                        page_token=None
                        ):
        """
        YouTube에서 주어진 매개변수에 따라 검색 요청을 수행.
        :param q: 검색어.
        :param search_type: 검색할 유형 (예: 비디오, 채널, 재생목록).
        :param order: 검색 결과의 정렬 순서.
        :param video_duration: 검색할 비디오의 길이.
        :param limit: 반환할 결과의 최대 개수.
        :param page_token: 다음 페이지 검색을 위한 토큰.
        :return: 검색된 Raw 데이터.
        """

        has_page_token = True if page_token else False
        if not has_page_token:
            searched_data = self._request_first_search(q, search_type, order, video_duration, limit, page_token)
        else:
            searched_data = self._request_next_page(page_token)

        return searched_data

    def _request_first_search(self,
                              q: str,
                              search_type: SearchType,
                              order: Order,
                              video_duration: VideoDuration,
                              limit=10,
                              page_token=None
                              ):
        """
        첫 페이지의 검색 결과를 요청.
        :param q: 검색어.
        :param search_type: 검색할 유형.
        :param order: 검색 결과의 정렬 순서.
        :param video_duration: 검색할 비디오의 길이.
        :param limit: 반환할 결과의 최대 개수.
        :param page_token: 다음 페이지 검색을 위한 토큰.
        :return: 검색된 첫 페이지의 Raw 데이터.
        """
        filter_builder = FilterBuilder()
        filter_builder.setOrder(order)
        filter_builder.setVideoDuration(video_duration)
        filter_builder.setSearchType(search_type)
        filter = filter_builder.build()

        endpoint = self.build_search_resource_url(q, filter)

        data = self._client.fetch_url(endpoint).decode('utf-8')

        # 2. 영상 페이지에서 데이터 추출
        context_data = YoutubeBasicInfoExtractor.extract_yt_initial_data(data)
        return context_data['init_data']

    def _request_next_page(self,
                           continuation_token: str
                           ):
        """
        다음 페이지의 검색 결과를 요청.
        :param continuation_token: 다음 페이지 검색을 위한 토큰.
        :return: 검색된 다음 페이지의 Raw 데이터.
        """
        url = self.build_search_v1_resource_url()
        data = json.dumps(DataParameterBuilder().set_continuation(continuation_token).build())
        response = self._client.fetch_url(url, data=data).decode("utf-8")
        searched_data = json.loads(response)
        return searched_data

    def _parse_data(self, raw_data):
        """
        검색된 Raw 데이터를 파싱하여 필요한 정보를 추출.
        :param raw_data: YouTube 검색 API로부터 받은 Raw 데이터.
        :return: 파싱된 데이터.
        """
        topbar_raw = try_get(raw_data, lambda x: x['topbar']['desktopTopbarRenderer'])
        topbar = YoutubeBasicInfoExtractor.extract_channel_topbar(topbar_raw)
        # 4.
        continuation_renderer = _search_attribute(raw_data, "continuationItemRenderer", max_depth=10)
        if continuation_renderer is not None:
            continuation_command_renderer_raw = try_get(continuation_renderer,
                                                        lambda x: x["continuationEndpoint"]["continuationCommand"],
                                                        dict)
            continuation_command_renderer = YoutubeBasicInfoExtractor.extract_continuation_command(continuation_command_renderer_raw)
        else:
            continuation_command_renderer = {}
        items = []
        item_section_renderer = _search_attributes(raw_data, "itemSectionRenderer", max_depth=10)
        if item_section_renderer is not None:
            video_renderers = _search_attributes(item_section_renderer, "videoRenderer") or []
            # playlist_renderer = _search_attributes(item_section_renderer, "playlistRenderer") or []
            # if playlist_renderer is not None:
            #     playlist = YoutubeBasicInfoExtractor.extract_playlist_renderer(playlist_renderer)
            #     items.append(playlist)
            for video_renderer_raw in video_renderers:
                video = YoutubeBasicInfoExtractor.extract_video_renderer(video_renderer_raw)
                video['kind'] = 'youtube#searchResult'
                items.append(video)

        return {
            'etag': None,
            'kind': self.KIND,
            'regionCode': topbar['country_code'],
            'items': items,
            'nextPageToken': try_get(continuation_command_renderer, lambda x:x['token']),
            'prevPageToken': None,
            'pageInfo': {
                'totalResults': len(items),
                'resultsPerPage': 20,
            }
        }
