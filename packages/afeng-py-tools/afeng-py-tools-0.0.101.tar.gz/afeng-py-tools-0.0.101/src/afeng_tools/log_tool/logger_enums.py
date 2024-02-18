"""
日志枚举
"""
from enum import Enum


class LoggerConfigKeyEnum(Enum):
    info_file = 'info_file'
    info_rotation = 'info_rotation'
    error_file = 'error_file'
    error_rotation = 'error_rotation'
