import os
import json
import requests
import logging
import datetime
import traceback

from collections import defaultdict

from src.utils import DB
from src.config import DEFAULT_LAST_DATE, LOGGER_NAME, DBFields
from src.utils import validate_ip_address, check_virus_total
from msticpy.transform.iocextract import IoCExtract

logger = logging.getLogger(LOGGER_NAME)


class Scraper:
    def __init__(self, base, start, last_blog_date, extractor: IoCExtract,
                 pdf_generator, db_handle: DB, upload, folder):
        self.base_url = base
        self.start_url = start
        self.blogs = dict()
        self.last_blog_date = last_blog_date if last_blog_date else DEFAULT_LAST_DATE
        self.extractor = extractor
        self.pdf_generator = pdf_generator
        self.db_handle = db_handle
        self.folder = os.path.join(folder, self.__class__.__name__)
        self.upload = upload
        self.accept_cookies_text = None
        os.makedirs(self.folder, exist_ok=True)

        self.all_sha256_hashes = self.db_handle.get_column(DBFields.SHA256.value)
        self.all_md5_hashes = self.db_handle.get_column(DBFields.MD5.value)

    def find_new_blogs(self):
        raise NotImplementedError

    def update_db(self, result, link):
        sha256_hash_found = set()
        md5_hash_found = set()

        if result.get('sha256_hash'):
            sha256_hash_found = result.get('sha256_hash')
        if result.get('md5_hash'):
            md5_hash_found = result.get('md5_hash')

        for h in sha256_hash_found.union(md5_hash_found):
            row_index = self.db_handle.get_index_of_row_with_value(h)
            if row_index:
                row = defaultdict(str, self.db_handle.get_row_by_number(row_index))
                if link not in row.get(DBFields.URLS.value):
                    row[DBFields.URLS.value] = f'{row[DBFields.URLS.value]};{link}'

                if not json.loads(row.get(DBFields.Existence_in_VT.value).lower()):
                    vt = check_virus_total(h)
                    if vt:
                        row[DBFields.SHA256.value] = vt[DBFields.SHA256.value]
                        row[DBFields.MD5.value] = vt[DBFields.MD5.value]
                        row[DBFields.Existence_in_VT.value] = 'True'
                        row[DBFields.Date_uploaded_to_vt.value] = vt[DBFields.Date_uploaded_to_vt.value]
                        row[DBFields.file_type.value] = vt[DBFields.file_type.value]
                        row[DBFields.meaningful_name.value] = vt[DBFields.meaningful_name.value]
                self.db_handle.update_row(row_index,
                                          row[DBFields.SHA256.value],
                                          row[DBFields.MD5.value],
                                          row[DBFields.first_scan_date.value],
                                          row[DBFields.URLS.value],
                                          row[DBFields.Existence_in_VT.value],
                                          row[DBFields.Date_uploaded_to_vt.value],
                                          row[DBFields.file_type.value],
                                          row[DBFields.meaningful_name.value])

            else:
                vt = check_virus_total(h)
                if vt:
                    data = defaultdict(str, vt)
                    data[DBFields.Existence_in_VT.value] = 'True'
                else:
                    data = defaultdict(str)
                    data[DBFields.Existence_in_VT.value] = 'False'
                    if h in sha256_hash_found:
                        data[DBFields.SHA256.value] = h
                    if h in md5_hash_found:
                        data[DBFields.MD5.value] = h
                data[DBFields.URLS.value] = link
                self.db_handle.add_row(data[DBFields.SHA256.value],
                                       data[DBFields.MD5.value],
                                       datetime.date.today().strftime('%d/%m/%Y'),
                                       data[DBFields.URLS.value],
                                       data[DBFields.Existence_in_VT.value],
                                       data[DBFields.Date_uploaded_to_vt.value],
                                       data[DBFields.file_type.value],
                                       data[DBFields.meaningful_name.value])

    def dump(self, name, content, pdf_bytes=None):
        logger.debug(f'starting dumping for {name}')
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

        for link, post_date in self.blogs.items():
            logger.debug(f'starting scraping for {link}')
            blog_name = self.get_post_name(link)
            pdf_bytes = None
            if self.pdf_generator:
                pdf_bytes = self.pdf_generator.generate_pdf_from_url(link, self.accept_cookies_text)
            page = requests.get(link)
            data = page.content.decode('utf-8')

            result = self.extractor.extract(src=data, defanged=False)
            self.update_db(result, link)
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
