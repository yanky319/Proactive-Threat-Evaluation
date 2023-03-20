import ipaddress


def validate_ip_address(ip_string):
    """
    :param ip_string: ipv4 or ipv6 address
    :return: True if input is a valid ip address
    """
    try:
        ipaddress.ip_address(ip_string)
        return True
    except ValueError:
        return False
