from datetime import datetime, timedelta

from src.scrapers import FortinetScraper, CybereasonScraper, SentineloneScraper, blog_scraper

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
    blog_scraper.extract_data(scraper)
    # scraper.check_blogs()
    # scraper = SentineloneScraper(last_blog_date=datetime.today() - timedelta(days=360))
    # scraper.find_new_blogs()
    for article in scraper.blogs:
        print(', '.join(article[0:2]), ', '.join([f"{k}: {len(v)} occurrence" for d in article[2:] for k, v in d.items()]), sep=', ')
