"""
日志配置
"""
import os.path

from afeng_tools.file_tool.tmp_file_tools import get_user_tmp_dir
from afeng_tools.log_tool.logger_enums import LoggerConfigKeyEnum

__LOGGER_CONFIG_CACHE__ = {
    LoggerConfigKeyEnum.info_file: os.path.join(get_user_tmp_dir(), '{time}-info.log'),
    LoggerConfigKeyEnum.info_rotation: '50 MB',
    LoggerConfigKeyEnum.error_file: os.path.join(get_user_tmp_dir(), '{time}-error.log'),
    LoggerConfigKeyEnum.error_rotation: '50 MB'
}


def set_config(config_key: LoggerConfigKeyEnum, config_value: str):
    """设置配置"""
    __LOGGER_CONFIG_CACHE__[config_key] = config_value


def get_config(config_key: LoggerConfigKeyEnum) -> str:
    """获取配置"""
    return __LOGGER_CONFIG_CACHE__.get(config_key)