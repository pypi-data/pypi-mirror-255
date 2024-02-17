from enum import Enum


class Order(Enum):
    """
    YouTube 검색 결과의 정렬 순서를 정의하는 Enum 클래스.
    """
    DATE = 'date'
    RATING = 'rating'
    RELEVANCE = 'relevance'
    VIEW_COUNT = 'viewCount'
    VIDEO_COUNT = 'videoCount'


class SearchType(Enum):
    """
    YouTube 검색 유형을 정의하는 Enum 클래스.
    """
    # VIDEO = 'SBBA'
    VIDEO = 'video'


class VideoDuration(Enum):
    """
    YouTube 검색에서 비디오 지속 시간을 필터링하기 위한 Enum 클래스.
    """
    ANY = 'any'
    SHORT = 'short'
    MEDIUM = 'medium'
    LONG = 'long'

    # ANY = ''
    # SHORT = 'BGAE='
    # MEDIUM = 'BGAM='
    # LONG = 'BGAI='


# class Order(Enum):
#     DATE = 'CAI'
#     RATING = 'CAE'
#     RELEVANCE = 'CAA'
#     VIEW_COUNT = 'CAM'
#     VIDEO_COUNT = 'CAM'
#
#
# class SearchType(Enum):
#     VIDEO = 'SBBA'
#
#
# class VideoDuration(Enum):
#     ANY = ''
#     SHORT = 'BGAE='
#     MEDIUM = 'BGAM='
#     LONG = 'BGAI='
#

def transform_order_to_code(order: Order):
    """
    주어진 Order Enum을 YouTube API 요청 코드로 변환.
    :param order: 변환할 Order Enum입니다.
    :return: YouTube API 요청에 사용될 문자열 코드.
    """
    if order == Order.DATE.value:
        return 'CAI'
    elif order == Order.RATING.value:
        return 'CAE'
    elif order == Order.RELEVANCE.value:
        return 'CAA'
    elif order == Order.VIEW_COUNT.value:
        return 'CAM'
    raise ValueError(f"not supported order: {order}")


def transform_search_type_to_code(order: Order, is_any_video_duration: bool):
    """
    주어진 SearchType Enum을 YouTube API 요청 코드로 변환.
    :param order: 변환할 SearchType Enum.
    :return: YouTube API 요청에 사용될 문자열 코드.
    """

    if order == SearchType.VIDEO.value:
        if is_any_video_duration:
            return 'SAhAB'
        else:
            return 'SBBA'
    return ''


# def transform_search_type_to_code(order: Order):
#     """
#     주어진 SearchType Enum을 YouTube API 요청 코드로 변환.
#     :param order: 변환할 SearchType Enum.
#     :return: YouTube API 요청에 사용될 문자열 코드.
#     """
#     if order == SearchType.VIDEO.value:
#         return 'CAI'
#     return


def transform_video_duration_to_code(duration: VideoDuration):
    """
    주어진 VideoDuration Enum을 YouTube API 요청 코드로 변환.
    :param duration: 변환할 VideoDuration Enum.
    :return: YouTube API 요청에 사용될 문자열 코드.
    """
    if duration == VideoDuration.ANY.value:
        return ''
    elif duration == VideoDuration.SHORT.value:
        return 'BGAE='
    elif duration == VideoDuration.MEDIUM.value:
        return 'BGAM='
    elif duration == VideoDuration.LONG.value:
        return 'BGAI='
    raise ValueError(f"not supported video duration: {duration}")


class FilterBuilder:
    """
        YouTube 검색 필터를 구성하기 위한 클래스입니다.
    """

    def __init__(self):
        self._order = Order.RELEVANCE.value
        self._search_type = SearchType.VIDEO.value
        self._video_duration = VideoDuration.ANY.value

    def setOrder(self, order: Order):
        self._order = order
        return self

    def setSearchType(self, search_type: SearchType):
        self._search_type = search_type

    def setVideoDuration(self, video_duration: VideoDuration):
        self._video_duration = video_duration

    def build(self):
        order_code = transform_order_to_code(self._order)
        is_any_video_duration = self._video_duration == 'any'
        search_type_code = transform_search_type_to_code(self._search_type, is_any_video_duration)
        video_duratin_code = transform_video_duration_to_code(self._video_duration)

        return f'{order_code}{search_type_code}{video_duratin_code}'
