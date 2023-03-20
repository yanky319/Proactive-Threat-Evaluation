import os
from datetime import datetime, timedelta

LOGGER_NAME = 'Proactive_Threat_Evaluation'


TEMP_FOLDER = os.path.join(os.getcwd(), 'temp')
os.makedirs(TEMP_FOLDER, exist_ok=True)


DEFAULT_LAST_DATE = (datetime.today() - timedelta(days=500))
ACCEPT_COOKIES_TEXTS = ['Accept All Cookies', 'Accept All', 'ACCEPT AND CLOSE']
