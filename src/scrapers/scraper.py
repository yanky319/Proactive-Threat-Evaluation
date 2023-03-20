import os
import json
import requests
import logging
import traceback

from src.config import DEFAULT_LAST_DATE, LOGGER_NAME
from src.utils import validate_ip_address

logger = logging.getLogger(LOGGER_NAME)


class Scraper:
    def __init__(self, base, start, last_blog_date, extractor, pdf_generator, upload, folder):
        self.base_url = base
        self.start_url = start
        self.blogs = []
        self.last_blog_date = last_blog_date if last_blog_date else DEFAULT_LAST_DATE
        self.extractor = extractor
        self.pdf_generator = pdf_generator
        self.folder = os.path.join(folder, self.__class__.__name__)
        self.upload = upload
        self.accept_cookies_text = None

        os.makedirs(self.folder, exist_ok=True)

    def find_new_blogs(self):
        raise NotImplementedError

    def dump(self, name, content, pdf_bytes=None):
        logger.info(f'starting dumping for {name}')
        ioc_file_path = os.path.join(self.folder, f'{name}.json')
        with open(ioc_file_path, "w") as json_outfile:
            json.dump(content, json_outfile, indent=0)  # , default=set_default)

        if pdf_bytes:
            try:
                pdf_file_path = os.path.join(self.folder, f'{name}.pdf')
                with open(pdf_file_path, "wb") as pdf_outfile:
                    pdf_outfile.write(pdf_bytes)
            except Exception as e:
                tb = traceback.format_exc()
                logger.error(f'Cannot create PDF file for {name}\nexception: {e}\ntraceback: {tb}')

        if self.upload:
            pass
        # TODO upload json and PDF files

    @staticmethod
    def get_post_name(url):
        """
        get name of post
        :param url: link to the post
        :return: name of the post
        """
        raise NotImplementedError

    def scrape(self):
        self.find_new_blogs()

        for url in self.blogs:
            logger.info(f'starting scraping for {url}')
            blog_name = self.get_post_name(url)
            pdf_bytes = None
            if self.pdf_generator:
                data, pdf_bytes = self.pdf_generator.generate_pdf_from_url(url, self.accept_cookies_text)
            else:
                page = requests.get(url)
                data = page.content.decode('utf-8')

            result = self.extractor.extract(src=data, defanged=False)
            # result['ipv4'] = list(filter(validate_ip_address, result['ipv4']))  # validate ipv4 address
            # result['ipv6'] = list(filter(validate_ip_address, result['ipv6']))  # validate ipv6 address
            # result.pop('linux_path') if result.get('linux_path') else None
            # result.pop('windows_path') if result.get('windows_path') else None

            self.dump(name=blog_name, content=self.validate_and_cleanup(result), pdf_bytes=pdf_bytes)

    @staticmethod
    def validate_and_cleanup(result):
        """
        validate the ioc's that need validation, erase the ones that are not needed, and remove empty values
        :param result: result of IoCExtract.extract.
        :return: clean dictionary of validated ioc's
        """
        keys_to_pop = ['linux_path', 'windows_path']
        keys_to_validate = {'ipv4': validate_ip_address}

        for key in keys_to_validate.keys():
            if result.get(key):
                result[key] = list(filter(keys_to_validate[key], result[key]))

        for key in keys_to_pop:
            result.pop(key) if result.get(key) else None

        return {key: list(val) for key, val in result.items() if val}
