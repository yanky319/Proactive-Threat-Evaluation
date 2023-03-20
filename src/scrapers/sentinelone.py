import requests
import logging

from bs4 import BeautifulSoup
from datetime import datetime

from src.config import LOGGER_NAME, TEMP_FOLDER
from src.scrapers.scraper import Scraper

logger = logging.getLogger(LOGGER_NAME)


class SentineloneScraper(Scraper):

    def __init__(self, extractor, pdf_generator, last_blog_date=None, upload=True, folder=TEMP_FOLDER):
        super().__init__(base='https://www.sentinelone.com{relative}',
                         start='/blog/category/cyber-response/',
                         last_blog_date=last_blog_date,
                         extractor=extractor,
                         pdf_generator=pdf_generator,
                         upload=upload,
                         folder=folder)
        self.accept_cookies_text = 'Accept All Cookies'

    @staticmethod
    def get_post_name(url):
        """
        get name of post
        :param url: link to the post
        :return: name of the post
        """
        return url.split('/')[-2]

    def find_new_blogs(self):
        dates = []
        page = requests.get(self.base_url.format(relative=self.start_url))
        soup = BeautifulSoup(page.content, "html.parser")
        # reports = soup.find_all("div", class_="primary-inner")
        articles = soup.find_all("article")
        for article in articles:
            a = article.find('a')
            link = a.get("href")
            date = a.find('div', class_='graphic').get('style')
            date_string = date[70:77:]

            date_object = datetime.strptime(date_string, '%Y/%m')

            if date_object > self.last_blog_date:
                self.blogs.append(link)
                dates.append(date_object)

        logger.debug(f'found {len(self.blogs)} blogs in {self.__class__.__name__}')

        if dates:
            self.last_blog_date = max(dates)
        else:
            self.last_blog_date = datetime.today()
