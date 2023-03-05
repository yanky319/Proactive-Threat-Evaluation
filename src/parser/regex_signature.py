import re

from .signature import Signature


class RegexSignature(Signature):
    def __init__(self, name, regex):
        super.__init__(name)
        self.regex = regex

    def extract(self, content):
        matches = re.findall(self.regex, content, re.IGNORECASE)
        return list(map(lambda x: {'name': self.name, 'artifact': x}, matches))
