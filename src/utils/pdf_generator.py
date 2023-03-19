import base64
import json
import time


from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class PdfGenerator:

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

    def generate_pdf_from_url(self, url, out_file=None):
        self.driver.get(url)

        time.sleep(1)  # allow the page to load, increase if needed
        try:
            WebDriverWait(self.driver, 10).until(ec.element_to_be_clickable((By.XPATH, "//*[text()='Accept All']"))).click()
        except Exception as e:
            # print(e)
            print(f"Maybe cookies are accepted for {url}")

        # self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        height = self.driver.execute_script("return document.body.scrollHeight")
        i = 100
        while i < height:
            self.driver.execute_script(f"window.scrollTo(0,{i})")
            i += 100
        self.driver.execute_script("window.scrollTo(0, document.body.scrollTop);")
        time.sleep(5)

        print_options = self.print_options.copy()
        result = self._send_devtools("Page.printToPDF", print_options)
        result = base64.b64decode(result['data'])

        if out_file:
            with open(out_file, "wb") as f:
                f.write(result)

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
