import os
import sys
import logging
from colorlog import ColoredFormatter


logs_path = os.path.join(os.getcwd(), 'logs.log')


def set_logger(name, Logs_path=logs_path, level=logging.DEBUG):
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
        logging.Formatter(fmt='%(asctime)s %(name)s %(levelname)s %(message)s', datefmt='%d/%m/%Y_%I:%M:%S-%p'))

    file_handler.setLevel(level)
    logger.addHandler(file_handler)

    logger.info(f'logger set: loges path is {logs_path}')

    return logger
