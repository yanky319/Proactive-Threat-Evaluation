from src.scrapers import FortinetScraper

if __name__ == '__main__':
    scraper = FortinetScraper()
    scraper.find_new_blogs()
    print(scraper.blogs)
