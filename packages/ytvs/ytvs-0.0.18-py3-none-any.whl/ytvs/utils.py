import logging
import re
# Unfavoured alias
import sys
import socket
import traceback
from datetime import datetime, timedelta
from typing import List, Any

from dateutil.relativedelta import relativedelta

from ytvs.compatible import COMPATIBLE_RE_PATTERN

logger = logging.getLogger(__name__)


compiled_regex_type = COMPATIBLE_RE_PATTERN

NO_DEFAULT = object()


def is_number_string(s):
    return s.isdigit()


def select_first_item_in_list(items: List[Any]):
    if len(items) > 0:
        item = items[0]
    else:
        item = None
    return item


def _search_attributes(obj, attr, max_depth=5):
    """
    Recursively find an attribute in a list or dictionary up to a specified depth.
    If one instance of the attribute is found, returns it directly.
    If multiple instances are found, returns them in a list.

    :param obj: The list or dictionary to search.
    :param attr: The attribute name to find.
    :param max_depth: The maximum depth to search.
    :return: The attribute value(s) if found, otherwise None.
    """

    def _find(obj, depth):
        if depth < 0:
            return []

        results = []

        if isinstance(obj, dict) and attr in obj:
            results.append(obj[attr])

        if isinstance(obj, (list, dict)):
            for element in obj.values() if isinstance(obj, dict) else obj:
                results.extend(_find(element, depth - 1))

        return results

    found = _find(obj, max_depth)
    if found:
        return found
    else:
        return None
    # if len(found) == 1:
    #     return found[0]
    # elif found:
    #     return found
    # else:
    #     return None


#
def _search_attribute(obj, attr, max_depth=1):
    """
    Recursively find an attribute in a list or dictionary up to a specified depth.

    :param obj: The list or dictionary to search.
    :param attr: The attribute name to find.
    :param max_depth: The maximum depth to search.
    :return: The attribute value if found, otherwise None.
    """
    if max_depth < 0:
        return None

    # Check if the current object itself has the attribute
    if isinstance(obj, dict) and attr in obj:
        return obj[attr]

    # If the object is a list or dictionary, iterate through its elements
    if isinstance(obj, (list, dict)):
        for element in obj.values() if isinstance(obj, dict) else obj:
            result = _search_attribute(element, attr, max_depth - 1)
            if result is not None:
                return result

    return None


def _search_regex(pattern, string, name, default=NO_DEFAULT, fatal=True, flags=0, group=None):
    """
    Perform a regex search on the given string, using a single or a list of
    patterns returning the first matching group.
    In case of failure return a default value or raise a WARNING or a
    RegexNotFoundError, depending on fatal, specifying the field name.
    """
    if isinstance(pattern, (str, str, compiled_regex_type)):
        mobj = re.search(pattern, string, flags)
    else:
        for p in pattern:
            mobj = re.search(p, string, flags)
            if mobj:
                break
    _name = name

    if mobj:
        if group is None:
            # return the first matching group
            return next(g for g in mobj.groups() if g is not None)
        elif isinstance(group, (list, tuple)):
            return tuple(mobj.group(g) for g in group)
        else:
            return mobj.group(group)
    elif default is not NO_DEFAULT:
        return default
    elif fatal:
        raise RegexNotFoundError('Unable to extract %s' % _name)
    else:
        return None


def is_korean_number(text):
    """
    Converts a Korean number with units like 천 (thousand) and 만 (ten thousand) into an integer.
    """
    # Regex to find number and unit
    match = re.search(r'(\d+(\.\d+)?)(천|만)', text)

    if match:
        return True
    else:
        return False


def convert_korean_number(text):
    """
    Converts a Korean number with units like 천 (thousand) and 만 (ten thousand) into an integer.
    """
    # Regex to find number and unit
    match = re.search(r'(\d+(\.\d+)?)(천|만)', text)

    if match:
        number = float(match.group(1))
        unit = match.group(3)

        # Convert based on Korean number system
        if unit == '만':
            number *= 10000
        elif unit == '천':
            number *= 1000

        return int(number)
    else:
        return None


def remove_non_numeric_korean(text):
    # 숫자, '백', '천', '만', '억'을 제외한 한글 삭제
    # 숫자와 콤마, 그리고 '백', '천', '만', '억'을 포함하는 정규표현식
    pattern = r'[^\d,백천만억]'

    # 정규표현식에 매칭되는 모든 한글을 삭제
    result = re.sub(pattern, '', text)

    return result


def extract_like_count(text):
    refined_text = text.replace(",", "")
    refined_text = remove_non_numeric_korean(refined_text)
    if not is_number_string(refined_text):
        logger.warning(f"Failed to extract like count from {text}")
        return 0
    return int(refined_text)


def extract_view_count(text):
    refined_text = text.replace(",", "")
    refined_text = remove_non_numeric_korean(refined_text)
    if not is_number_string(refined_text):
        logger.warning(f"Failed to extract view count from {text}")
        return 0
    return int(refined_text)
    # 숫자(콤마 포함)와 선택적으로 '백', '천', '만', '억'을 찾는 정규표현식
    # pattern = r'\d+(백|천|만|억)?'
    # pattern = r'\d'
    #
    # # 정규표현식에 매칭되는 모든 부분을 찾아 리스트로 반환
    # matches = re.findall(pattern, refined_text)
    #
    # # 찾은 부분들에서 불필요한 그룹을 제거하고 문자열로 변환
    # result = ' '.join(match[0] + match[2] for match in matches)
    # return result


def int_or_none(v, scale=1, default=None, get_attr=None, invscale=1):
    if get_attr:
        if v is not None:
            v = getattr(v, get_attr, None)
    if v in (None, ''):
        return default
    try:
        return int(v) * invscale // scale
    except (ValueError, TypeError, OverflowError):
        return default


def str_to_int(int_str):
    if isinstance(int_str, int):
        return int_str
    elif isinstance(int_str, str):
        int_str = re.sub(r'[,\.\+]', '', int_str)
        return int_or_none(int_str)


def try_get(src, getter, expected_type=None):
    if not isinstance(getter, (list, tuple)):
        getter = [getter]
    for get in getter:
        try:
            v = get(src)
        except (AttributeError, KeyError, TypeError, IndexError):
            pass
        else:
            if expected_type is None or isinstance(v, expected_type):
                return v


def number_str_abbr_to_int(int_str):
    try:
        count = convert_korean_number(int_str)
        if count is None:
            count = ''.join(filter(str.isdigit, int_str))
        return count
    except Exception as e:
        return None


class YoutubeDLError(Exception):
    """Base exception for YoutubeDL errors."""
    pass


class UnavailableVideoError(YoutubeDLError):
    """Unavailable Format exception.

    This exception will be thrown when a video is requested
    in a format that is not available for that video.
    """
    pass


class ExtractorError(YoutubeDLError):
    """Error during info extraction."""

    def __init__(self, msg, tb=None, expected=False, cause=None, video_id=None):
        """ tb, if given, is the original traceback (so that it can be printed out).
        If expected is set, this is a normal error message and most likely not a bug in youtube-dl.
        """

        if sys.exc_info()[0] in (compat_urllib_error.URLError, socket.timeout, UnavailableVideoError):
            expected = True
        if video_id is not None:
            msg = video_id + ': ' + msg
        if cause:
            msg += ' (caused by %r)' % cause
        if not expected:
            msg += ""
        super(ExtractorError, self).__init__(msg)

        self.traceback = tb
        self.exc_info = sys.exc_info()  # preserve original exception
        self.cause = cause
        self.video_id = video_id

    def format_traceback(self):
        if self.traceback is None:
            return None
        return ''.join(traceback.format_tb(self.traceback))


class RegexNotFoundError(ExtractorError):
    """Error when a regex didn't match"""
    pass



def remove_prefix_with_colon_in_date_text(text:str):
    # 정규표현식 패턴: 줄의 시작 부분부터 ':' 문자가 나오기 전까지의 모든 문자와 ':' 자체
    pattern = r'^[^:]+:'

    # 각 줄을 순회하면서 패턴에 해당하는 부분 제거
    lines = text.split('\n')
    result = []
    for line in lines:
        # 패턴이 있는지 확인
        if re.search(pattern, line):
            # 패턴을 제거하고 결과에 추가
            new_line = re.sub(pattern, '', line)
            result.append(new_line)
        else:
            # 패턴이 없는 경우 원래의 줄을 결과에 추가
            result.append(line)

    return '\n'.join(result)



def convert_relative_to_absolute_date(date):
    """
    날짜 포맷을 년.월.일. 형식으로 변경하는 함수
    네이버 뉴스의 경우
    0분전, 0시간 전, 0일전 등 7일 내 뉴스는
    년.월.일이 아닌 다른 포맷으로 표시되므로 날짜를 통일해주는 함수가 필요함
    """
    current_time = datetime.now()
    date = date.replace(" ", "")
    date = date.replace("(수정됨)", "")
    date = date.replace("스트리밍시간:", "")
    date = date.replace("스트리밍시작:", "")
    date = date.replace("최초공개:", "")
    date = remove_prefix_with_colon_in_date_text(date)
    if date.endswith('분전'):
        minutes = int(date[:-2])
        date = current_time - timedelta(minutes=minutes)

    elif date.endswith('시간전'):
        hours = int(date[:-3])
        date = current_time - timedelta(hours=hours)

    elif date.endswith('일전'):
        days = int(date[:-2])
        date = current_time - timedelta(days=days)

    elif date.endswith('주전'):
        weeks = int(date[:-2])
        date = current_time - timedelta(weeks=weeks)

    elif date.endswith('개월전'):
        months = int(date[:-3])
        date = current_time - relativedelta(months=months)

    elif date.endswith('년전'):
        years = int(date[:-2])
        date = current_time - relativedelta(years=years)

    else:
        date = datetime.strptime(date, '%Y.%m.%d.')
    return date.strftime("%Y-%m-%d")
