import json
import logging
import datetime
import requests
import traceback

from src.config import DBFields, VT_BASE_URL, VT_HEADERS, LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


def check_virus_total(found_hash):
    """
    search virus total with a hash for more info
    :param found_hash:
    :return: dictionary with found data about the hash
    """

    try:
        response = requests.get(VT_BASE_URL.format(hash=found_hash), headers=VT_HEADERS)
        if response.status_code == 401:
            logger.warning(f'got Unauthorized to search virus total')
        elif response.status_code == 200:
            result = json.loads(response.text)['data']

            first_submission_date_unix_timestamp = result['attributes']['first_submission_date']
            first_submission_date = datetime.datetime.fromtimestamp(first_submission_date_unix_timestamp)

            # TODO check if this is malware_bazaar or not
            meaningful_name = result['attributes']['meaningful_name']

            return {DBFields.SHA256.value: result['attributes']['sha256'],
                    DBFields.MD5.value: result['attributes']['md5'],
                    DBFields.Date_uploaded_to_vt.value: first_submission_date,
                    DBFields.file_type.value: result['attributes']['type_description'],
                    DBFields.malware_bazaar.value: meaningful_name}
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f'Error in check_virus_total with {found_hash}\nexception: {e}\ntraceback: {tb}')


