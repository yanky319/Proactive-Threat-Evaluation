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
        page = requests.get(self.base_url.format(relative=self.start_url))
        soup = BeautifulSoup(page.content, "html.parser")
        reports = soup.find_all("div", class_="container container-is-blog columns is-multiline page-center")
        for report in reports:
            a = report.find(class_='text-content-bundle').find('a')
            link = a.get("href")

            date_string = report.find(class_='text-content-bundle').find_all("p")[-1].find_all("span")[0].get_text()[:-2]
            date_object = datetime.strptime(date_string, '%B %d, %Y')

            if date_object > self.last_blog_date:
                self.blogs.append((link, date_object.strftime("%d/%m/%Y")))

        logger.debug(f'found {len(self.blogs)} blogs in {self.__class__.__name__}')


x = CybereasonScraper()
x.find_new_blogs()
