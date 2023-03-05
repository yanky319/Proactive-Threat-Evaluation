from .parser import Parser
from .regex_signature import RegexSignature
from .config import IP_PATTERN, IP_RANGE_PATTERN


class IpParser(Parser):

    def __init__(self):
        super.__init__()

        ip = RegexSignature(
            name='ip',
            regex=IP_PATTERN
        )

        ip_range = RegexSignature(
            name='ip_range',
            regex=IP_RANGE_PATTERN
        )

        self.add_signature(ip)
        self.add_signature(ip_range)
