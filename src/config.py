import os
from enum import Enum
from datetime import datetime, timedelta

LOGGER_NAME = 'Proactive_Threat_Evaluation'

BASE_FOLDER = os.path.abspath('..')
TEMP_FOLDER = os.path.join(BASE_FOLDER, 'temp')
os.makedirs(TEMP_FOLDER, exist_ok=True)


DEFAULT_LAST_DATE = (datetime.today() - timedelta(days=100))
ACCEPT_COOKIES_TEXTS = ['Accept All Cookies', 'Accept All', 'ACCEPT AND CLOSE']


################################################################
# data base
################################################################
class DBFields(Enum):
    SHA256 = 'SHA256'
    MD5 = 'MD5'
    first_scan_date = 'First scan date'
    URLS = 'Blog URLs'
    Existence_in_VT = 'Existence in VT'
    Date_uploaded_to_vt = 'Date uploaded to VT'
    file_type = 'File type'
    meaningful_name = 'Meaningful name'


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
