import re
import requests
import logging

from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from src.config import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


class SecuritySoupScraper:

    def __init__(self, last_blog_date=(datetime.today() - timedelta(days=7))):

        self.base_url = 'https://security-soup.net{relative}'
        self.start_url = ''
        self.blogs = []
        self.last_blog_date = last_blog_date

    def find_new_blogs(self):
        dates = []
        page = requests.get(self.base_url.format(relative=self.start_url))
        soup = BeautifulSoup(page.content, "html.parser")
        articles = soup.find_all('article')
        for article in articles:
            a = article.find('header').find(class_="entry-meta").find(class_="posted-on").find('a')
            link = a.get('href')
            date_string = a.find(class_='entry-date published').get_text()
            date_object = datetime.strptime(date_string, '%B %d, %Y')
            articleID = article.get('id')

            if date_object > self.last_blog_date:
                self.blogs.append(link)
                dates.append(date_object)

            logger.debug(f'found {len(self.blogs)} blogs in {self.__class__.__name__}')

            if dates:
                self.last_blog_date = max(dates)
            else:
                self.last_blog_date = datetime.today()
