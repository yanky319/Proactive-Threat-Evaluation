import logging
import re

import requests

from src.config import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)

IP_PATTERN = re.compile(r'(\d{1,3}(\[\.\]|\.)){3}\d{1,3}(:\d{1,5})?')
MD5_PATTERN = re.compile(r'\b([a-fA-F\d]{32})\b')  # MD5 hash (32 hexadecimal digits):
SHA1_PATTERN = re.compile(r'\b([a-fA-F\d]{40})\b')  # SHA-1 hash (40 hexadecimal digits):
SHA256_PATTERN = re.compile(r'\b([a-fA-F\d]{64})\b')  # SHA-256 hash (64 hexadecimal digits):


def extract_regex(scraper, pattern_name, pattern):
    match_list = []
    for i in range(len(scraper.blogs)):
        page = requests.get(scraper.blogs[i][0])
        j = 0
        while j < len(page.text):
            try:
                match = pattern.search(page.text[j:])
                if match is None:
                    break
                match_list.append(match.group())
                j += match.end()
            except:
                logger.debug("No more matches of {}".format(pattern_name))
                pass
        logger.info('found {} matches for {} in {}'.format(len(match_list), pattern_name, scraper.blogs[i][0]))
        scraper.blogs[i].append({pattern_name: match_list})


def extract_data(scraper):
    extract_regex(scraper, 'IP_PATTERN', IP_PATTERN)
    extract_regex(scraper, 'MD5_PATTERN', MD5_PATTERN)
    extract_regex(scraper, 'SHA1_PATTERN', SHA1_PATTERN)
    extract_regex(scraper, 'SHA256_PATTERN', SHA256_PATTERN)
