import datetime
import os
import json
import requests
import logging
import traceback
import pickle

from src.config import DEFAULT_LAST_DATE, LOGGER_NAME
from src.utils import validate_ip_address
import openpyxl as excelDB

logger = logging.getLogger(LOGGER_NAME)


def create_new_sheet(wb, blog_name):
    if len(wb.sheetnames) == 1 and wb.sheetnames[0] == 'Sheet':
        wb['Sheet'].title = blog_name
    else:
        wb.create_sheet(blog_name)
    ws = wb[blog_name]
    ws.cell(row=1, column=1).value = 'Scan date'
    ws.cell(row=1, column=2).value = 'Blog upload date'
    ws.cell(row=1, column=3).value = 'URL'
    ws.cell(row=1, column=4).value = 'SHA256'
    ws.cell(row=1, column=5).value = 'MD5'
    ws.cell(row=1, column=6).value = 'Existence_in_VT'
    ws.cell(row=1, column=7).value = 'Date_uploaded_to_vt'
    ws.cell(row=1, column=8).value = 'file_type'
    ws.cell(row=1, column=9).value = 'malware_bazaar'
    return ws


# def save_result_object_to_file(result):
#     with open('result.file', 'wb') as result_file:
#         pickle.dump(result, result_file)
#
#
# def load_result_object_from_file():
#     with open("..\\" + 'result.file', 'rb') as result_file:
#         return pickle.load(result_file)


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

    def update_db(self, result, url):
        root_path = r'C:\Users\uziel.shemesh\PycharmProjects\Proactive-Threat-Evaluation'
        db_path = os.path.join(root_path, 'IOCs_DB.xlsx')
        # Load in the workbook
        try:
            wb = excelDB.load_workbook(db_path)
        except:
            wb = excelDB.Workbook()  # if Excel file not exist create new
        # Get a sheet by name
        blog_name = self.__class__.__name__
        if blog_name not in wb.sheetnames:
            blog_sheet = create_new_sheet(wb, blog_name)
        else:
            blog_sheet = wb[blog_name]
        current_row = blog_sheet.max_row + 1
        blog_sheet.cell(row=current_row, column=1).value = datetime.date.today().strftime('%d/%m/%Y')
        try:
            blog_sheet.cell(row=current_row, column=2).value = self.last_blog_date.strftime('%d/%m/%Y')
        except Exception as e:
            print(f'blog_name - {e}')
        blog_sheet.cell(row=current_row, column=3).value = url
        try:
            blog_sheet.cell(row=current_row, column=4).value = ';'.join(result.get('sha256_hash'))
        except Exception as e:
            print(f'blog_name - {e}')
        try:
            blog_sheet.cell(row=current_row, column=5).value = ';'.join(result.get('md5_hash'))
        except Exception as e:
            print(f'blog_name - {e}')
        blog_sheet.cell(row=current_row, column=6).value = 'exist_in_VT'  # TODO check existing in VT
        blog_sheet.cell(row=current_row, column=7).value = 'date_uploaded_to_vt'  # TODO check upload date to VT
        blog_sheet.cell(row=current_row, column=8).value = 'file_type'  # TODO check file type from VT
        blog_sheet.cell(row=current_row, column=9).value = 'malware_bazaar'  # TODO get data from 'malware bazaar'
        wb.save(db_path)

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
            # x = result, url, self.__class__.__name__, self.folder, self.last_blog_date
            # save_result_object_to_file(x)
            # exit(100)
            self.update_db(result, url)
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

# def update_db(self, result, url):
#     db_path = os.path.join(self[1], 'IOCs_DB.xlsx')
#     # Load in the workbook
#     try:
#         wb = excelDB.load_workbook(db_path)
#     except:
#         wb = excelDB.Workbook()  # if Excel file not exist create new
#     # Get a sheet by name
#     blog_name = self[0]
#     if blog_name not in wb.sheetnames:
#         blog_sheet = create_new_sheet(wb, blog_name)
#     else:
#         blog_sheet = wb[blog_name]
#     current_row = blog_sheet.max_row + 1
#
#     blog_sheet.cell(row=current_row, column=1).value = datetime.date.today().strftime('%d/%m/%Y')
#     blog_sheet.cell(row=current_row, column=2).value = self[2].strftime('%d/%m/%Y')
#     blog_sheet.cell(row=current_row, column=3).value = url
#     blog_sheet.cell(row=current_row, column=4).value = ';'.join(result.get('sha256_hash'))
#     blog_sheet.cell(row=current_row, column=5).value = ';'.join(result.get('md5_hash'))
#     blog_sheet.cell(row=current_row, column=6).value = 'exist_in_VT'  # TODO check existing in VT
#     blog_sheet.cell(row=current_row, column=7).value = 'date_uploaded_to_vt'  # TODO check upload date to VT
#     blog_sheet.cell(row=current_row, column=8).value = 'file_type'  # TODO check file type from VT
#     blog_sheet.cell(row=current_row, column=9).value = 'malware_bazaar'  # TODO get data from 'malware bazaar'
#     wb.save(db_path)
#
#
# x = load_result_object_from_file()
# print(x)
# self = x[2:5]
# update_db(self, x[0], x[1])  # x = result, url, self.__class__.__name__, self.folder, self.last_blog_date
#
# # def update_db(self, result, url):
