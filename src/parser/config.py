###################################################
# regex
###################################################
MD5_PATTERN = r'\b([a-fA-F\d]{32})\b'  # MD5 hash (32 hexadecimal digits):
SHA1_PATTERN = r'\b([a-fA-F\d]{40})\b'  # SHA-1 hash (40 hexadecimal digits):
SHA256_PATTERN = r'\b([a-fA-F\d]{64})\b'  # SHA-256 hash (64 hexadecimal digits):

IP_PATTERN = r'(\d{1,3}(\[\.\]|\.)){3}\d{1,3}(:\d{1,5})?'
IP_RANGE_PATTERN = r''  # TODO
