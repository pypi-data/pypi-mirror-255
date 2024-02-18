import logging
import os
from pathlib import Path

from afeng_tools.log_tool import logger_settings
from afeng_tools.log_tool.logger_enums import LoggerConfigKeyEnum


def get_logger(log_name, store: bool = True):
    """
    创建logger
    :param log_name: 日志名称
    :param log_file: 日志文件
    :param store: 存储日志至本地
    :return: Logger
    """
    log_file = logger_settings.get_config(LoggerConfigKeyEnum.info_file)
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)
    stream = logging.StreamHandler()
    stream.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(levelname)s %(asctime)s] %(message)s')
    stream.setFormatter(formatter)
    logger.addHandler(stream)
    if store is True:
        os.makedirs(Path(log_file).parent, exist_ok=True)
        logfile = logging.FileHandler(log_file, mode='a')
        logfile.setLevel(logging.INFO)
        logfile.setFormatter(formatter)
        logger.addHandler(stream)
    return logger
