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

logger = logging.getLogger(LOGGER_NAME)


class Scraper:
    def __init__(self, base, start, last_blog_date, extractor, pdf_generator, db_handle: DB, upload, folder):
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

        self.all_sha256_hashes = self.db_handle.get_column('SHA256')
        self.all_md5_hashes = self.db_handle.get_column('MD5')

    def find_new_blogs(self):
        raise NotImplementedError

    def add_from_dict(self, data, link, post_date):
        data = defaultdict(str, data)
        self.db_handle.add_row(datetime.date.today().strftime('%d/%m/%Y'),
                               post_date.strftime('%d/%m/%Y'),
                               link,
                               data[DBFields.SHA256.value],
                               data[DBFields.MD5.value],
                               data[DBFields.Existence_in_VT.value],
                               data[DBFields.Date_uploaded_to_vt.value],
                               data[DBFields.file_type.value],
                               data[DBFields.malware_bazaar.value])

    def update_db(self, result, link, post_date):
        md5_found = []

        if result.get('sha256_hash'):
            for sha_256 in result.get('sha256_hash'):
                added = False
                if sha_256 in self.all_sha256_hashes:
                    row = self.db_handle.get_row_with_value(sha_256)
                    if row.get(DBFields.Existence_in_VT.value) \
                            and json.loads(row.get(DBFields.Existence_in_VT.value).lower()):
                        self.add_from_dict(row, link, post_date)
                        md5_found.append(row[DBFields.MD5.value])
                        added = True

                if not added:
                    vt = check_virus_total(sha_256)
                    if vt:
                        vt[DBFields.Existence_in_VT.value] = 'True'
                        self.add_from_dict(vt, link, post_date)

                        self.all_sha256_hashes.append(sha_256)
                        self.all_md5_hashes.append(vt[DBFields.MD5.value])
                        md5_found.append(vt[DBFields.MD5.value])
                    else:
                        self.add_from_dict({DBFields.SHA256.value: sha_256,
                                            DBFields.Existence_in_VT.value: 'False'},
                                           link, post_date)

        if result.get('md5_hash'):
            for md5 in [h for h in result.get('md5_hash') if h not in md5_found]:
                added = False
                if md5 in self.all_md5_hashes:
                    row = self.db_handle.get_row_with_value(md5)
                    if row.get(DBFields.Existence_in_VT.value) \
                            and json.loads(row.get(DBFields.Existence_in_VT.value).lower()):
                        self.add_from_dict(row, link, post_date)
                        added = True

                if not added:
                    vt = check_virus_total(md5)
                    if vt:
                        vt[DBFields.Existence_in_VT.value] = 'True'
                        self.add_from_dict(vt, link, post_date)
                        self.all_md5_hashes.append(md5)
                        self.all_sha256_hashes.append(vt[DBFields.SHA256.value])
                    else:
                        self.add_from_dict({DBFields.MD5.value: md5,
                                            DBFields.Existence_in_VT.value: 'False'},
                                           link, post_date)

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
                data, pdf_bytes = self.pdf_generator.generate_pdf_from_url(link, self.accept_cookies_text)
            else:
                page = requests.get(link)
                data = page.content.decode('utf-8')

            result = self.extractor.extract(src=data, defanged=False)
            self.update_db(result, link, post_date)
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
