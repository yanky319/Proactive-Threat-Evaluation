import requests
import logging

from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from src.config import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


class FortinetScraper:

    def __init__(self, last_blog_date=(datetime.today() - timedelta(days=7))):
        self.base_url = 'https://www.fortinet.com{relative}'
        self.start_url = '/blog/threat-research'
        self.blogs = []
        self.last_blog_date = last_blog_date

    def find_new_blogs(self):
        dates = []
        page = requests.get(self.base_url.format(relative=self.start_url))
        soup = BeautifulSoup(page.content, "html.parser")
        reports = soup.find_all("div", class_="b3-blog-list__post text-container")
        for report in reports:
            a = report.find(class_='b3-blog-list__title').find('a')
            link = self.base_url.format(relative=a.get("href"))

            date_string = report.find(class_='b3-blog-list__meta').find_all("span")[-1].get_text()
            date_object = datetime.strptime(date_string, '%B %d, %Y')

            if date_object > self.last_blog_date:
                self.blogs.append(link)
                dates.append(date_object)

        logger.debug(f'found {len(self.blogs)} blogs in {self.__class__.__name__}')

        if dates:
            self.last_blog_date = max(dates)
        else:
            self.last_blog_date = datetime.today()


if __name__ == '__main__':
    scraper = FortinetScraper()
    scraper.find_new_blogs()
    print(len(scraper.blogs))
    print(len(set(scraper.blogs)))
