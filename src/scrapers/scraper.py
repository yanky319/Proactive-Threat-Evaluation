import os
import json
import requests


class Scraper:
    def __init__(self, base, start, last_blog_date, extractor, pdf_generator, upload, folder):
        self.base_url = base
        self.start_url = start
        self.blogs = []
        self.last_blog_date = last_blog_date
        self.extractor = extractor
        self.pdf_generator = pdf_generator
        self.folder = os.path.join(folder, self.__class__.__name__)
        self.upload = upload

        os.makedirs(self.folder, exist_ok=True)

    def find_new_blogs(self):
        raise NotImplementedError

    def dump(self, name, content, pdf_bytes=None):
        ioc_file_path = os.path.join(self.folder, f'{name}.json')
        with open(ioc_file_path, "w") as json_outfile:
            json.dump(content, json_outfile)

        if pdf_bytes:
            pdf_file_path = os.path.join(self.folder, f'{name}.pdf')
            with open(pdf_file_path, "wb") as pdf_outfile:
                json.dump(content, pdf_outfile)

        if self.upload:
            pass
        # TODO upload json and PDF files

    def get_blog_name(self, url):
        raise NotImplementedError

    def scrape(self):
        self.find_new_blogs()

        for url in self.blogs:
            blog_name = self.get_blog_name(url)
            pdf_bytes = None
            if self.pdf_generator:
                data, pdf_bytes = self.pdf_generator.generate_pdf_from_url(url)
            else:
                page = requests.get(url)
                data = page.content.decode('utf-8')

            result = self.extractor.extract(src=data)

            self.dump(name=blog_name, content=result, pdf_bytes=pdf_bytes)
