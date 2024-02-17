import logging
from string import Template

# 현재 모듈에 대한 로거를 설정합니다.
logger = logging.getLogger(__name__)


class EmbeddingIFrameAPICreator:
    # Embedding을 위한 iframe API HTML의 템플릿을 정의.
    IFRAME_HTML_TEMPLATE = """
            <iframe width="560" height="315" src="https://www.youtube.com/embed/{}" title="YouTube video 
            player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; 
            picture-in-picture; web-share" allowfullscreen></iframe> """

    def __init__(self):
        # YouTube의 기본 임베딩 URL을 설정합니다.
        self.base_url = 'https://www.youtube.com/embed'

    @classmethod
    def create(cls, video_id: str):
        """임베딩한 URL을 생성하고 반환"""
        # video_id가 문자열이 아닌 경우 ValueError를 발생
        if not isinstance(video_id, str):
            raise ValueError("Parameter video_id must be str type")
        # string.Template을 사용하여 iframe HTML 템플릿을 생성
        template = Template(cls.IFRAME_HTML_TEMPLATE)
        # video_id를 사용하여 IFrame HTML을 생성
        iframe_html = template.substitute(video_id=video_id)
        return iframe_html
