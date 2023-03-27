import requests
import logging

from bs4 import BeautifulSoup
from datetime import datetime

from src.config import LOGGER_NAME, TEMP_FOLDER
from src.scrapers.scraper import Scraper

logger = logging.getLogger(LOGGER_NAME)


class KasperskyScraper(Scraper):

    def __init__(self, extractor, pdf_generator,  db_handle, last_blog_date=None, upload=True, folder=TEMP_FOLDER):
        super().__init__(base='https://www.kaspersky.com{relative}',
                         start='/blog/category/threats/',
                         last_blog_date=last_blog_date,
                         extractor=extractor,
                         pdf_generator=pdf_generator,
                         db_handle=db_handle,
                         upload=upload,
                         folder=folder)
        self.accept_cookies_text = 'ACCEPT AND CLOSE'

    @staticmethod
    def get_post_name(url):
        """
        get name of post
        :param url: link to the post
        :return: name of the post
        """
        return url.split('/')[-3]

    def find_new_blogs(self):
        dates = []
        page = requests.get(self.base_url.format(relative=self.start_url))
        soup = BeautifulSoup(page.content, "html.parser")
        articles = soup.find_all('div', class_='c-card__content')
        for article in articles:
            link = article.find(class_='c-card__title').find('a').get('href')
            date_string = article.find(class_='c-card__time').find('time').get_text()
            date_object = datetime.strptime(date_string, '%B %d, %Y')

            if date_object > self.last_blog_date:
                self.blogs[link] = date_object
                dates.append(date_object)

        logger.info(f'found {len(self.blogs)} blogs in {self.__class__.__name__}')

        if dates:
            self.last_blog_date = max(dates)
        else:
            self.last_blog_date = datetime.today()
