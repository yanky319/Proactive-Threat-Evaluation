import requests
import logging

from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from src.config import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


class CybereasonScraper:

    def __init__(self, last_blog_date=(datetime.today() - timedelta(days=7))):

        self.base_url = 'https://www.cybereason.com{relative}'
        self.start_url = '/blog/category/research'
        self.blogs = []
        self.last_blog_date = last_blog_date

    def find_new_blogs(self):
        dates = []
        page = requests.get(self.base_url.format(relative=self.start_url))
        soup = BeautifulSoup(page.content, "html.parser")
        reports = soup.find_all("div", class_="text-content-bundle")
        for report in reports:
            a = report.find('a', class_='post-name')
            link = a.get("href")

            date_string = report.find('span', class_='publish-date').get_text()
            date_object = datetime.strptime(date_string, '%B %d, %Y /')

            if date_object > self.last_blog_date:
                self.blogs.append(link)
                dates.append(date_object)

        logger.debug(f'found {len(self.blogs)} blogs in {self.__class__.__name__}')
        if dates:
            self.last_blog_date = max(dates)
        else:
            self.last_blog_date = datetime.today()
