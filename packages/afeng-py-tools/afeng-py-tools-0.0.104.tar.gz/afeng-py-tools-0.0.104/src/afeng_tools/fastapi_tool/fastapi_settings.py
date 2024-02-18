"""
FastAPI设置
"""

from typing import Callable

from afeng_tools.fastapi_tool.core.fastapi_enums import FastapiConfigKeyEnum

__FASTAPI_CONFIG_CACHE__ = dict()

from afeng_tools.fastapi_tool.core.fastapi_items import FastapiConfigItem


def init_config(fastapi_config_item: FastapiConfigItem):
    """初始化配置"""
    _set_config(FastapiConfigKeyEnum.is_json_api, fastapi_config_item.is_json_api)
    _set_config(FastapiConfigKeyEnum.error404_context_data_func, fastapi_config_item.error404_context_data_func)
    _set_config(FastapiConfigKeyEnum.error500_context_data_func, fastapi_config_item.error500_context_data_func)
    _set_config(FastapiConfigKeyEnum.error501_context_data_func, fastapi_config_item.error501_context_data_func)
    _set_config(FastapiConfigKeyEnum.error500_background_work_func, fastapi_config_item.error500_background_work_func)


def _set_config(config_key: FastapiConfigKeyEnum, config_value: str | Callable | bool):
    """设置配置"""
    __FASTAPI_CONFIG_CACHE__[config_key] = config_value


def get_config(config_key: FastapiConfigKeyEnum) -> str | Callable:
    """获取配置"""
    return __FASTAPI_CONFIG_CACHE__.get(config_key)
