import re
import requests
import logging

from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from src.config import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


class SentineloneScraper:

    def __init__(self, last_blog_date=(datetime.today() - timedelta(days=7))):

        self.base_url = 'https://www.sentinelone.com{relative}'
        self.start_url = '/blog/category/cyber-response/'
        self.blogs = []
        self.last_blog_date = last_blog_date

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

            date_pattern = r'\d{4}/\d{2}'

            match = re.search(date_pattern, date)
            if match:
                date_string = match.group()
                date_object = datetime.strptime(date_string, '%Y/%m')

                if date_object > self.last_blog_date:
                    self.blogs.append(link)
                    dates.append(date_object)

            logger.debug(f'found {len(self.blogs)} blogs in {self.__class__.__name__}')

            if dates:
                self.last_blog_date = max(dates)
            else:
                self.last_blog_date = datetime.today()
