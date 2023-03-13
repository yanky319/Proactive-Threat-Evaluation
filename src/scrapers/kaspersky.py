import re
import requests
import logging

from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from src.config import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


class KasperskyScraper:

    def __init__(self, last_blog_date=(datetime.today() - timedelta(days=7))):

        self.base_url = 'https://www.kaspersky.com{relative}'
        self.start_url = '/blog/category/threats/'
        self.blogs = []
        self.last_blog_date = last_blog_date

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
                self.blogs.append(link)
                dates.append(date_object)

            logger.debug(f'found {len(self.blogs)} blogs in {self.__class__.__name__}')

            if dates:
                self.last_blog_date = max(dates)
            else:
                self.last_blog_date = datetime.today()


