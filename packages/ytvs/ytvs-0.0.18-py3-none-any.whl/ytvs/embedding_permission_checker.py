import base64
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver as wired_webdriver
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from seleniumwire import webdriver
from ytvs.embedding_iframe_api_creator import EmbeddingIFrameAPICreator


class EmbeddingPermissionChecker:

    def __init__(self):
        self._embedding_url_creator = EmbeddingIFrameAPICreator()

    def is_embeddable(self, video_id: str):

        iframe_api = self._embedding_url_creator.create(video_id)
        encoded_html = base64.b64encode(iframe_api.encode('utf-8'))
        data_url = f"data:text/html;base64,{encoded_html.decode('utf-8')}"

        options = webdriver.ChromeOptions()
        options.add_argument('--disable-dev-shm-usage')
        is_headless = True
        if is_headless is True:
            options.add_argument('headless')
            options.add_argument('--no-sandbox')

        driver = wired_webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(data_url)
        wait = WebDriverWait(driver, 100)
        iframe = wait.until(EC.visibility_of_element_located((By.TAG_NAME, "iframe")))

        # iframe 요소 찾기 및 전환
        driver.switch_to.frame(iframe)
        iframe_html = driver.page_source
        soup = BeautifulSoup(iframe_html, "html.parser", from_encoding="utf-8")
        error_container_elem = soup.find("div", {'class': 'ytp-error'})

        if error_container_elem is not None:
            return False
        return True


