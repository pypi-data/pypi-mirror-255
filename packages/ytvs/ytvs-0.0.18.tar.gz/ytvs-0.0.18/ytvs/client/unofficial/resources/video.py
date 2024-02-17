import re
from difflib import SequenceMatcher

import requests
from bs4 import BeautifulSoup
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common import NoSuchElementException
from seleniumwire import webdriver as wired_webdriver
from selenium import webdriver
from seleniumwire import webdriver, utils
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC

from ytvs.client.unofficial.resources import SearchResource
from ytvs.client.unofficial.resources.base_resource import Resource
from ytvs.embedding_permission_checker import EmbeddingPermissionChecker
from ytvs.extractor import YoutubeBasicInfoExtractor
from ytvs.filter import SearchType, Order, VideoDuration
from ytvs.utils import try_get, str_to_int, _search_attribute, _search_attributes


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


class VideoResource(Resource):
    KIND = 'youtube#video'

    def get_video_by_id(self, video_id: str):
        """
        주어진 비디오 ID에 대한 YouTube 비디오 정보를 조회.
        :param video_id: 정보를 가져올 비디오의 ID.
        :return: 파싱된 비디오 정보.
        """
        # 1. 영상 페이지 요청
        data = self._request_data(video_id)

        # 2. 영상 페이지에서 데이터 추출
        yt_initial_data = YoutubeBasicInfoExtractor.extract_yt_initial_data(data)

        # 3. 데이터 분석 및 파싱
        parsed_data = self._parse_video_data_from_initial_data(yt_initial_data)
        parsed_data_from_html = self._parsed_video_data_from_html_txt(data)

        embeddable_checker = EmbeddingPermissionChecker()
        # is_embeddable = embeddable_checker.is_embeddable(video_id)

        # 4. 추가 데이터 병합
        parsed_data['items'][0]['id'] = video_id
        parsed_data['items'][0]['snippet']['publishedAt'] = parsed_data_from_html['published_date']
        parsed_data['items'][0]['status'] = {}
        # parsed_data['items'][0]['status']['embeddable'] = is_embeddable
        #
        # title = parsed_data['items'][0]['snippet']['title']
        # thumbnails_and_duration = self._search_video_thumbnails_and_duration(title)
        #
        # parsed_data['items'][0]['snippet']['thumbnails'] = thumbnails_and_duration['thumbnails']
        # parsed_data['items'][0]['contentDetails'] = {}
        # parsed_data['items'][0]['contentDetails']['duration'] = thumbnails_and_duration['duration']

        # 5. 반환
        return parsed_data

    def _search_video_thumbnails_and_duration(self, title):
        # @NOTE: Youtube 검색 API를 이용시, '#' 문자가 있으면 올바르게 검색되지 않는 이슈로 제거함
        # 하지만, # 문자가 포함되어있는경우, 검색이 안되는 정확한 원인파악이 필요
        # -> Youtube 페이지에서는 #이 있어도 검색이 정확하게됨.(API 쿼리 구문에 # 이포함됨. 차이가 뭐지)

        refined_title = title.replace("#", "")
        search_resource = SearchResource(self._client)
        searched = search_resource.search(q=refined_title, search_type=SearchType.VIDEO.value,
                                          order=Order.RELEVANCE.value,
                                          video_duration=VideoDuration.ANY.value)
        searched_item = self._find_by_title_in_search_list(title, searched['items'])
        if searched_item is not None:
            duration = searched['items'][0]['snippet']['duration']
            thumbnails = searched['items'][0]['snippet']['thumbnails']
        else:
            duration = None
            thumbnails = None
        return {
            'duration': duration,
            'thumbnails': thumbnails
        }

    def _find_by_title_in_search_list(self, title: str, searches):
        # 제목이 가장 유사한 녀석을 찾음
        most_similarity = 0
        most_similarity_idx = 0
        for i, searched_item in enumerate(searches[:5]):
            searched_item_title = searched_item['snippet']['title']
            similarity = similar(searched_item_title, title)

            if similarity > most_similarity:
                most_similarity = similarity
                most_similarity_idx = i
        if most_similarity > 0.7:
            return searches[most_similarity_idx]
        else:
            return None

    def _request_data(self, video_id: str):
        """
        YouTube 비디오 페이지의 HTML 데이터를 요청.
        :param video_id: 요청할 비디오의 ID.
        :return: 비디오 페이지의 HTML 텍스트를 반환.
        """
        # 1. Video resource 요청 URL 생성
        url = self.build_video_resource_url(video_id)

        # # 2. Video 페이지 요청 및 데이터 추출
        return self._client.fetch_url(url).decode("utf-8")

    def _parsed_video_data_from_html_txt(self, html_text):
        # *******
        soup = BeautifulSoup(html_text, "html.parser", from_encoding="utf-8")
        # date published
        published_date_text = soup.find("meta", itemprop="datePublished")['content']
        # get the duration of the video
        # 광고 영상때문에, HTML 페이지에서는 확실한 영상의 재생시간 획득을 보장할수가 없음...
        # video_duration_text = soup.find("span", {"class": "ytp-time-duration"}).text
        return {'published_date': published_date_text}

    def _parse_video_data_from_initial_data(self, initial_data):
        """
        초기 데이터에서 YouTube 비디오 데이터를 파싱.
        :param initial_data: YouTube 비디오 페이지에서 추출된 초기 데이터.
        :return: 파싱된 비디오 데이터를 반환.
        """
        # 1. 데이터 분석 및 파싱
        contents = try_get(initial_data,
                           lambda x: x['init_data']['contents']['twoColumnWatchNextResults']['results']['results'][
                               'contents'], list) or []

        # 2. Content 획득
        video_primary_video_renderer = _search_attribute(contents, "videoPrimaryInfoRenderer")
        if video_primary_video_renderer:
            video = YoutubeBasicInfoExtractor.extract_video(video_primary_video_renderer)
        else:
            video = {}
        video_secondary_info_renderer = _search_attribute(contents, "videoSecondaryInfoRenderer")
        if video_secondary_info_renderer:
            description = try_get(video_secondary_info_renderer,
                                  lambda x: x['attributedDescription']['content'], str)
            owner = try_get(video_secondary_info_renderer,
                            lambda x: x['owner']['videoOwnerRenderer'], dict)
            owner = YoutubeBasicInfoExtractor.extract_video_owner_renderer(owner)
        else:
            description = None
            owner = {}

        item_section_renderers = _search_attributes(contents, 'itemSectionRenderer')
        comments_header_renderer = _search_attribute(item_section_renderers, "commentsEntryPointHeaderRenderer",
                                                     max_depth=6)
        comments_header = YoutubeBasicInfoExtractor.extract_comments_header_renderer(comments_header_renderer)

        return {
            'etag': None,
            'kind': 'youtube#videoListResponse',
            'items': [{
                'kind': self.KIND,
                'localizations': None,
                'etag': None,
                'snippet': {
                    'title': try_get(video, lambda x: x['title'], str),
                    'categoryId': None,
                    'channelId': try_get(owner, lambda x: x['channel_id'], str),
                    'channelTitle': try_get(owner, lambda x: x['title'], str),
                    'description': description,
                    'liveBroadcastContent': None,
                    'localized': None,
                    'publishedAt': try_get(video, lambda x: x['published_at'], str),
                    'tags': [],
                    'thumbnails': None,
                    'hashtags': try_get(video, lambda x: x['super_title_links'], list)
                },
                'statistics': {
                    'dislikeCount': None,
                    'commentCount': try_get(comments_header, lambda x: x['comment_count']),
                    'likeCount': try_get(video, lambda x: x['like_count']),
                    'viewCount': try_get(video, lambda x: x['view_count']),
                }
            }],
            'nextPageToken': None,
            'prevPageToken': None,
            'pageInfo': {
                'totalResults': 1,
                'resultsPerPage': 1
            }
        }
