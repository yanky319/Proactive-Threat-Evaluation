import inspect
import src.scrapers

from src.utils import set_logger, get_config, set_config
from src.config import LOGGER_NAME
from src import BlogScrapper

logger = set_logger(LOGGER_NAME)

if __name__ == '__main__':
    config = get_config()
    blogs = []
    for name, obj in inspect.getmembers(src.scrapers):
        if inspect.isclass(obj):  # TODO
            if config.get(name) and config.get(name).get('last_blog_date'):
                scrapper = obj(last_blog_date=config.get(name).get('last_blog_date'))
            else:
                scrapper = obj()
            scrapper.find_new_blogs()
            bs = BlogScrapper()
            bs.extract_data(scrapper)
            blogs.append(bs)

            if not config.get(name):
                config[name] = dict()
            config[name]['last_blog_date'] = scrapper.last_blog_date
            for post in bs.posts:
                for i in post.IPv4_OBFUSCATED:
                    print(i, sep=", ")
                # post.print_post(5)
    set_config(config)
