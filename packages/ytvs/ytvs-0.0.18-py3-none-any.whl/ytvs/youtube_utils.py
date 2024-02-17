"""
    This provide some common utils methods for YouTube resource.
"""
import base64

import isodate
from isodate.isoerror import ISO8601Error

from pyyoutube.error import ErrorMessage, PyYouTubeException

from ytvs import proto


def get_video_duration(duration: str) -> int:
    """
    ISO 8601 형식의 비디오 지속 시간을 초 단위로 변환합니다. 이 형식은 YouTube API에서 비디오 지속 시간을 표현하는 데 사용됩니다.
    예: 'PT14H23M42S'는 '14시간 23분 42초'를 나타냅니다.

    Args:
        duration (str): ISO 8601 형식의 비디오 지속 시간입니다.

    Returns:
        int: 지속 시간을 초 단위로 나타낸 정수값입니다.

    예외 처리:
        ISO8601Error: 지속 시간의 형식이 잘못되었을 때 발생합니다.
    """
    try:
        seconds = isodate.parse_duration(duration).total_seconds()
        return int(seconds)
    except ISO8601Error as e:
        raise PyYouTubeException(
            ErrorMessage(
                status_code=10001,
                message=f"Exception in convert video duration: {duration}. errors: {e}",
            )
        )


def _make_comment_ctoken(video_id, sort=0, offset=0, lc='', secret_key=''):
    """
    YouTube 댓글 페이지의 Continuation Token을 생성.
    :param video_id: 비디오 ID.
    :param sort: 댓글 정렬 방식.
    :param offset: 댓글 페이지의 오프셋.
    :param lc: 로케일 설정.
    :param secret_key: 보안 키.
    :return: 생성된 Continuation Token.
    """
    # 비디오 ID와 보안 키를 바이트로 변환
    video_id = proto.as_bytes(video_id)
    secret_key = proto.as_bytes(secret_key)

    # 페이지 정보 구성
    page_info = proto.string(4, video_id) + proto.uint(6, sort)
    offset_information = proto.nested(4, page_info) + proto.uint(5, offset)
    if secret_key:
        offset_information = proto.string(1, secret_key) + offset_information

    page_params = proto.string(2, video_id)
    if lc:
        page_params += proto.string(6, proto.percent_b64encode(proto.string(15, lc)))

    result = proto.nested(2, page_params) + proto.uint(3, 6) + proto.nested(6, offset_information)
    return base64.urlsafe_b64encode(result).decode('ascii')
