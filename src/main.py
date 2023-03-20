from msticpy.transform.iocextract import IoCExtract

from src.scrapers import *
from src.utils import set_logger, get_config, set_config, PdfGenerator
from src.config import LOGGER_NAME

logger = set_logger(LOGGER_NAME)


def main():
    config = get_config()
    scrapers = [FortinetScraper, SentineloneScraper, CybereasonScraper, KasperskyScraper, SecuritySoupScraper]
    # scrapers = [CybereasonScraper]
    extractor = IoCExtract()
    pdf_generator = PdfGenerator()
    for scraper in scrapers:
        name = scraper.__name__
        if config.get(name) and config.get(name).get('last_blog_date'):
            scrapper = scraper(
                extractor=extractor,
                pdf_generator=pdf_generator,
                last_blog_date=config.get(name).get('last_blog_date')
            )
        else:
            scrapper = scraper(
                extractor=extractor,
                pdf_generator=pdf_generator
            )
        scrapper.scrape()

        if not config.get(name):
            config[name] = dict()
        config[name]['last_blog_date'] = scrapper.last_blog_date

    set_config(config)


if __name__ == '__main__':
    main()
