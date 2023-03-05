import os

LOGGER_NAME = 'Proactive_Threat_Evaluation'


TEMP_FOLDER = os.path.join(os.getcwd(), 'temp')
os.makedirs(TEMP_FOLDER, exist_ok=True)

