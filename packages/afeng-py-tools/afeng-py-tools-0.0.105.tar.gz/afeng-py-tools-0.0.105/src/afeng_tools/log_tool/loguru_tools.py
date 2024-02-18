"""
loguru工具类： pip install loguru  -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
"""
import traceback

from loguru import logger

from afeng_tools.log_tool import logger_settings
from afeng_tools.log_tool.logger_enums import LoggerConfigKeyEnum


def get_logger():
    logger.add(logger_settings.get_config(LoggerConfigKeyEnum.info_file),
               rotation=logger_settings.get_config(LoggerConfigKeyEnum.info_rotation), compression='zip',
               encoding='utf-8', level='INFO')
    logger.add(logger_settings.get_config(LoggerConfigKeyEnum.error_file),
               rotation=logger_settings.get_config(LoggerConfigKeyEnum.error_rotation), compression='zip',
               encoding='utf-8', level='WARNING')
    return logger


def log_error(log, error_msg: str, ex: Exception = None):
    """记录错误日志"""
    if ex:
        log.error(f'{error_msg}:{ex}\n {traceback.format_exc()}')
    else:
        log.error(f'{error_msg}\n {traceback.format_exc()}')
