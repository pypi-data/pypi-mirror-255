# YouTube API와 통신을 위한 기본 설정 값들을 정의

# 기본 API 키: YouTube API를 사용하기 위한 기본 키입니다.
DEFAULT_API_KEY = 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'

# 모바일 사용자 에이전트: YouTube 요청을 모바일 기기에서 발생한 것처럼 표시하기 위한 사용자 에이전트입니다.
MOBILE_USER_AGENT = 'Mozilla/5.0 (Linux; Android 7.0; Redmi Note 4 Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Mobile Safari/537.36'
# 모바일 사용자 에이전트 헤더: HTTP 요청에 사용될 모바일 사용자 에이전트 헤더입니다.
MOBILE_USER_AGENT_HEADER = (('User-Agent', MOBILE_USER_AGENT),)

# 데스크톱 사용자 에이전트: YouTube 요청을 데스크톱 기기에서 발생한 것처럼 표시하기 위한 사용자 에이전트입니다.
DESKTOP_USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0'
# 데스크톱 사용자 에이전트 헤더: HTTP 요청에 사용될 데스크톱 사용자 에이전트 헤더입니다.
DESKTOP_USER_AGENT_HEADER = (('User-Agent', DESKTOP_USER_AGENT),)

# JSON 콘텐츠 타입 헤더: HTTP 요청 시 JSON 형식의 콘텐츠를 사용함을 나타냅니다.
CONTENT_TYPE_JSON_HEADER = (('Content-Type', 'application/json'),)

# 데스크톱 XHR 헤더: 데스크톱 환경에서 YouTube API와 통신할 때 사용되는 HTTP 헤더입니다.
DESKTOP_XHR_HEADERS = (
    ('Accept', '*/*'),
    ('Accept-Language', 'en-US,en;q=0.5'),
    ('X-YouTube-Client-Name', '1'),
    ('X-YouTube-Client-Version', '2.20180830'),
) + DESKTOP_USER_AGENT_HEADER

# 모바일 XHR 헤더: 모바일 환경에서 YouTube API와 통신할 때 사용되는 HTTP 헤더입니다.
MOBILE_XHR_HEADERS = (
    ('Accept', '*/*'),
    ('Accept-Language', 'en-US,en;q=0.5'),
    ('X-YouTube-Client-Name', '2'),
    ('X-YouTube-Client-Version', '2.20180830'),
) + MOBILE_USER_AGENT_HEADER