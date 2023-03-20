import base64
import json
import time
import traceback
import logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from src.config import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


class PdfGenerator:
    """
    class holding a selenium web driver to print web pages using printToPDF method
    """

    # https://chromedevtools.github.io/devtools-protocol/tot/Page#method-printToPDF
    print_options = {
        'landscape': False,
        'displayHeaderFooter': False,
        'printBackground': True,
        'preferCSSPageSize': True,
        'paperWidth': 6.97,
        'paperHeight': 16.5,
    }

    def __init__(self):
        options = ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')

        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=options
        )

    def generate_pdf_from_url(self, url, accept_cookies_text, out_file=None):
        """

        :param url: the page to print to PDF
        :param accept_cookies_text: text of the "accept cookies" button
        :param out_file: if specified the pdf will pe saved there
        :return: tuple(page html, bytes of the pdf)
        """
        self.driver.get(url)
        time.sleep(1)  # allow the page to load, increase if needed
        self.click_button_with_text(accept_cookies_text)

        # self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        height = self.driver.execute_script("return document.body.scrollHeight")
        i = 50
        while i < height:
            self.driver.execute_script(f"window.scrollTo(0,{i})")
            i += 50
        self.driver.execute_script("window.scrollTo(0, document.body.scrollTop);")
        time.sleep(5)

        print_options = self.print_options.copy()
        result = self._send_devtools("Page.printToPDF", print_options)
        result = base64.b64decode(result['data'])

        if out_file:
            try:
                with open(out_file, "wb") as f:
                    f.write(result)
            except Exception as e:
                tb = traceback.format_exc()
                logger.error(f'error with saving pdf bytes\nexception: {e}\ntraceback: {tb}')

        return self.driver.page_source, result

    def _send_devtools(self, cmd, params):
        """
        Works only with chromedriver.
        Method uses cromedriver's api to pass various commands to it.
        """
        resource = "/session/%s/chromium/send_command_and_get_result" % self.driver.session_id
        url = self.driver.command_executor._url + resource
        body = json.dumps({'cmd': cmd, 'params': params})
        response = self.driver.command_executor._request('POST', url, body)
        return response.get('value')

    def click_button_with_text(self, button_text):
        """
        click button with the given text if it shows up
        :param button_text:
        :return:
        """
        if button_text:
            try:
                WebDriverWait(self.driver, 10).until(
                    ec.element_to_be_clickable((By.XPATH, f"//*[text()='{button_text}']"))).click()
            except Exception:
                pass
