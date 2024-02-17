from enum import Enum


class LanguageCode(Enum):
    EN = 'en'
    KO = 'ko'
    # 여기에 추가 언어 코드를 정의할 수 있습니다.


class RegionCode(Enum):
    US = 'US'
    KR = 'KR'
    # 여기에 추가 국가 코드를 정의할 수 있습니다.


class DataParameterBuilder:
    """
    YouTube API 요청에 필요한 데이터 매개변수를 구성하기 위한 빌더 클래스.
    이 클래스를 사용하여 유연하게 매개변수를 설정 가능.
    """

    def __init__(self):
        # 기본 매개변수 설정
        self._params = {
            'context': {
                'client': {
                    'hl': 'ko',  # 기본 언어 설정 (en 영어)
                    'gl': 'KR',  # 기본 지역 설정 (US 미국)
                    'clientName': 'WEB',
                    'clientVersion': '2.20210804.02.00',
                },
            },
        }

    def set_language(self, language: LanguageCode):
        """
        사용할 언어를 설정.
        :param language: 설정할 언어 코드 (예: 'ko', 'en')
        :return: 빌더 객체 자신을 반환 (메서드 체이닝을 위함).
        """
        self._params['context']['client']['hl'] = language.value
        return self

    def set_region(self, region: RegionCode):
        """
        사용할 지역을 설정.
        :param region: 설정할 지역 코드 (예: 'KR', 'US')
        :return: 빌더 객체 자신을 반환.
        """
        self._params['context']['client']['gl'] = region.value
        return self

    def set_continuation(self, continuation):
        """
        Continuation 토큰을 설정.
        :param continuation: 설정할 continuation 토큰 값.
        :return: 빌더 객체 자신을 반환.
        """
        self._params['continuation'] = continuation.replace('=', '%3D')
        return self

    def set_param(self, param):
        """
        파라미터 값을 설정.
        :param param: 설정할 파라미터 값.
        :return: 빌더 객체 자신을 반환.
        """
        self._params['params'] = param.replace('=', '%3D')
        return self

    def build(self):
        """
        설정된 매개변수를 바탕으로 최종 데이터 매개변수 객체를 생성.
        :return: 생성된 데이터 매개변수 객체.
        """
        return self._params
