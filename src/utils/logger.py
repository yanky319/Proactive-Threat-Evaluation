import os
import sys
import logging
import datetime
from colorlog import ColoredFormatter

from src.config import TEMP_FOLDER, LOGGER_NAME


path = os.path.join(TEMP_FOLDER, f'{datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")}.txt')


def set_logger(name, logs_path=path, level=logging.DEBUG):
    # from sys import gettrace
    # if gettrace() is not None:
    #     level = logging.DEBUG
    # else:
    #     level = logging.INFO

    logger = logging.getLogger(name)
    logger.setLevel(level)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(ColoredFormatter(
        '%(log_color)s%(asctime)-8s%(reset)s |'
        ' %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s'))
    logger.addHandler(stdout_handler)

    # file handler
    file_handler = logging.FileHandler(logs_path)
    file_handler.setFormatter(
        logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s', datefmt='%d/%m/%Y_%I:%M:%S-%p'))
    # logging.Formatter(fmt='%(asctime)s %(name)s %(levelname)s %(message)s', datefmt='%d/%m/%Y_%I:%M:%S-%p'))

    file_handler.setLevel(level)
    logger.addHandler(file_handler)

    logger.info(f'logger set: loges path is {logs_path}')

    return logger


if __name__ == '__main__':
    _logger = set_logger(LOGGER_NAME)
    _logger.info('info')
    _logger.warning('warning')
    _logger.error('error')
    _logger.debug('debug')
