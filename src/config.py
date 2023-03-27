import os
from enum import Enum
from datetime import datetime, timedelta

LOGGER_NAME = 'Proactive_Threat_Evaluation'

BASE_FOLDER = os.path.abspath('..')
TEMP_FOLDER = os.path.join(BASE_FOLDER, 'temp')
os.makedirs(TEMP_FOLDER, exist_ok=True)


DEFAULT_LAST_DATE = (datetime.today() - timedelta(days=500))
ACCEPT_COOKIES_TEXTS = ['Accept All Cookies', 'Accept All', 'ACCEPT AND CLOSE']


################################################################
# data base
################################################################
class DBFields(Enum):
    Scan_date = 'Scan date'
    Blog_upload_date = 'Blog upload date'
    URL = 'URL'
    SHA256 = 'SHA256'
    MD5 = 'MD5'
    Existence_in_VT = 'Existence_in_VT'
    Date_uploaded_to_vt = 'Date_uploaded_to_vt'
    file_type = 'file_type'
    malware_bazaar = 'malware_bazaar'


DB_FOLDER = os.path.join(BASE_FOLDER, 'DB')
os.makedirs(DB_FOLDER, exist_ok=True)
DB_PATH = os.path.join(DB_FOLDER, 'IOCs_DB.xlsx')

SHEET_NAME = 'post results'

################################################################
# virus total
################################################################
vt_api_key = os.getenv('vt_apikey')
VT_BASE_URL = "https://www.virustotal.com/api/v3/files/{hash}"
VT_HEADERS = {
    "accept": "application/json",
    "x-apikey": vt_api_key
}
