import logging
import re
import requests

from src.config import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)

IP_PATTERN = re.compile(r'(\d{1,3}(\[\.\]|\.)){3}\d{1,3}(:\d{1,5})?')
IPv6_PATTERN = re.compile(r'(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}')
MD5_PATTERN = re.compile(r'\b([a-fA-F\d]{32})\b')  # MD5 hash (32 hexadecimal digits):
SHA1_PATTERN = re.compile(r'\b([a-fA-F\d]{40})\b')  # SHA-1 hash (40 hexadecimal digits):
SHA256_PATTERN = re.compile(r'\b([a-fA-F\d]{64})\b')  # SHA-256 hash (64 hexadecimal digits):
URL_PATTERN = re.compile(
    r"(https?://(?:www(\[\.\]|\.)|(?!www))[^\s.]+(\[\.\]|\.)[^\s]{2,}|www(\[\.\]|\.)[^\s]+(\[\.\]|\.)[^\s]{2,})")
IPv4_OBFUSCATED_PATTERN = re.compile(r'(\d{1,3}(\[\.\]|\.|\\056)){3}\d{1,3}(:\d{1,5})?')


class Post:
    def __init__(self, url):
        self.url = url
        self.IPv4s = []
        self.IPv4_OBFUSCATED = []
        self.IPv6s = []
        self.URLs = []
        self.MD5s = []
        self.SHA1s = []
        self.SHA256s = []

    def print_post(self, length):
        print(self.url)
        print("IPs: {ips}, URLs: {urls}, MD5s: {md5}, SHA1s: {sha1}, SHA256s: {sha256}".format(ips=len(self.IPv4s),
                                                                                               urls=len(self.URLs),
                                                                                               md5=len(self.MD5s),
                                                                                               sha1=len(self.SHA1s),
                                                                                               sha256=len(
                                                                                                   self.SHA256s)))
        print("IPS: ")
        for i in self.IPv4s[:length]:
            print(i, sep="\t")
        print("URLs: ")
        for i in self.URLs[:length]:
            print(i, sep="\t")
        print("MD5s: ")
        for i in self.MD5s[:length]:
            print(i, sep="\t")
        print("SHA1: ")
        for i in self.SHA1s[:length]:
            print(i, sep=",\t")
        print("SHA256: ")
        for i in self.SHA256s[:length]:
            print(i, sep="\t")


class BlogScrapper:

    def __init__(self):
        self.posts = []

    def extract_regex(self, post, list, pattern_name, pattern):
        match_list = []
        j = 0
        while j < len(post.text):
            try:
                match = pattern.search(post.text[j:])
                if match is None:
                    break
                match_list.append(match.group())
                j += match.end()
            except:
                logger.debug("No more matches of {}".format(pattern_name))
                pass
        logger.info('found {} matches for {} in {}'.format(len(match_list), pattern_name, post.url))
        list.extend(match_list)

    def extract_data(self, scraper):
        for i in range(len(scraper.blogs)):
            post = requests.get(scraper.blogs[i])
            res = Post(post.url)
            self.extract_regex(post, res.URLs, 'URLs', URL_PATTERN)
            self.extract_regex(post, res.IPv4s, 'IPs', IP_PATTERN)
            self.extract_regex(post, res.MD5s, 'MD5s', MD5_PATTERN)
            self.extract_regex(post, res.SHA1s, 'SHA1s', SHA1_PATTERN)
            self.extract_regex(post, res.SHA256s, 'SHA256s', SHA256_PATTERN)
            self.extract_regex(post, res.IPv6s, 'IPv6s', IPv6_PATTERN)
            self.extract_regex(post, res.IPv4_OBFUSCATED, 'IPv6s', IPv4_OBFUSCATED_PATTERN)
            self.posts.append(res)
