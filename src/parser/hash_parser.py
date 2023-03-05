from .parser import Parser
from .regex_signature import RegexSignature
from .config import SHA256_PATTERN, SHA1_PATTERN, MD5_PATTERN


class HashParser(Parser):

    def __init__(self):
        super.__init__()

        sha_256 = RegexSignature(
            name='sha_256',
            regex=SHA256_PATTERN
        )

        sha_1 = RegexSignature(
            name='sha_1',
            regex=SHA1_PATTERN
        )

        md5 = RegexSignature(
            name='md5',
            regex=MD5_PATTERN
        )

        self.add_signature(sha_256)
        self.add_signature(sha_1)
        self.add_signature(md5)

