from datetime import datetime, timedelta

from src.scrapers import FortinetScraper, CybereasonScraper

from src.utils.logger import set_logger
from src.config import LOGGER_NAME

logger = set_logger(LOGGER_NAME)

if __name__ == '__main__':
    # logger.info('info')
    # logger.warning('warning')
    # logger.error('error')
    # logger.debug('debug')
    # scraper = FortinetScraper()
    # scraper.find_new_blogs()
    scraper = CybereasonScraper(last_blog_date=datetime.today() - timedelta(days=180))
    scraper.find_new_blogs()
    print(scraper.blogs)
