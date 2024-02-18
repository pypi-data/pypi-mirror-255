"""
配置工具类
"""
import logging
import os
import tempfile
from datetime import datetime
from typing import Any

from afeng_tools.application_tool import application_tools
from afeng_tools.application_tool.settings_enum import SettingsKeyEnum, SettingsStaticItem
from afeng_tools.python_tool import dict_tools

# 程序配置
APP_CONFIG_CACHE = {}
# 程序配置参数，如：{root}代表项目根目录
APP_CONFIG_PARAMS = {}


def init_config_param(**kwargs) -> dict:
    """
    初始化配置参数， 如：init_config_param(root=ROOT_PATH, resource=RESOURCE_PATH)
    :param kwargs: 如：root=‘路径’， 则可以在yaml配置文件中使用{root}替换路径
    :return: 程序配置参数
    """
    APP_CONFIG_PARAMS.update(kwargs)
    # 用户目录
    APP_CONFIG_PARAMS['user_home'] = os.path.expanduser('~')
    # 临时目录
    APP_CONFIG_PARAMS['tmp'] = tempfile.gettempdir()
    APP_CONFIG_PARAMS['date'] = datetime.today().strftime('%Y%m%d')
    return kwargs


def _format_param(config_value: Any):
    """格式化参数，如：替换配置中的{root}为根路径"""
    if config_value is not None and isinstance(config_value, str):
        for tmp_key in APP_CONFIG_PARAMS:
            if '{' + tmp_key + '}' in config_value:
                config_value = config_value.replace('{' + tmp_key + '}', str(APP_CONFIG_PARAMS.get(tmp_key)))
    return config_value


def _get_config(config_dict: dict, key_enum: SettingsKeyEnum):
    if '.' in key_enum.value.name:
        return dict_tools.tree_get_value(config_dict, key_enum.value.name.split('.'))
    return config_dict.get(key_enum.value.name)


def _init_static_config(config_dict: dict):
    """初始化静态文件配置"""
    app_static_value = config_dict.get(SettingsKeyEnum.server_static.value.name)
    if app_static_value:
        if isinstance(app_static_value, list):
            app_static_value = [SettingsStaticItem(name=tmp.get('name'), url=tmp.get('url'),
                                                   path=_format_param(tmp.get('path')))
                                for tmp in app_static_value]
        elif isinstance(app_static_value, dict):
            app_static_value = SettingsStaticItem(name=app_static_value.get('name'),
                                                  url=app_static_value.get('url'),
                                                  path=_format_param(app_static_value.get('path')))
        config_dict[SettingsKeyEnum.server_static.value.name] = app_static_value
    return config_dict


def _check_config(config_dict: dict, is_reload: bool = False) -> bool:
    """检查配置：用于检查配置项是否有问题"""
    error_msg_list = []
    is_web = _get_config(config_dict, SettingsKeyEnum.app_is_web)
    for tmp_enum in SettingsKeyEnum.__iter__():
        if (not is_web and tmp_enum.name.startswith('server_')) or tmp_enum == SettingsKeyEnum.server_static:
            continue
        settings_key_item = tmp_enum.value
        config_value = _get_config(config_dict, tmp_enum)
        if settings_key_item.is_required:
            if config_value is None:
                error_msg_list.append(f"缺少必要的配置参数[{settings_key_item.name}], "
                                      f"该参数用于配置[{settings_key_item.comment}]")
        if _get_config(config_dict, tmp_enum) is not None:

            if not isinstance(config_value, settings_key_item.value_type):
                error_msg_list.append(
                    f"配置参数[{settings_key_item.name}]的值类型不对，需要的值类型是{settings_key_item.value_type}, "
                    f"现在配置的值类型是[{type(config_value)}]")
    if error_msg_list:
        error_msg = "\t\n".join(error_msg_list)
        if is_reload:
            logging.error(f'配置文件配置有问题：\n\t{error_msg}')
            return False
        raise ValueError(f'配置文件配置有问题：\n\t{error_msg}')
    return True


def _init_config_default_value(config_dict: dict) -> dict:
    """初始化设置配置默认值"""
    for tmp_enum in SettingsKeyEnum.__iter__():
        tmp_key_item = tmp_enum.value
        if tmp_key_item.default is not None and config_dict.get(tmp_key_item.name) is None:
            # 如果为None，设置为默认值
            config_dict[tmp_key_item.name] = tmp_key_item.default
    return config_dict


def init_load_config(yaml_file, is_reload: bool = False) -> dict:
    """
    初始化配置
    :param yaml_file: yaml配置我呢见
    :param is_reload: 是否是重新加载配置
    :return:
    """
    result = application_tools.read_all_config(yaml_file)
    APP_CONFIG_PARAMS['app_code'] = result.get(SettingsKeyEnum.app_code.value.name)
    # 设置配置默认值
    result = _init_config_default_value(result)
    # 格式化参数
    for tmp_key in result.keys():
        result[tmp_key] = _format_param(result.get(tmp_key))
    # 初始化静态文件配置
    result = _init_static_config(result)
    # 格式配置（组装一下上下级关系）
    result = dict_tools.format_config_dict(result)
    # 检查配置
    if _check_config(result, is_reload=is_reload):
        APP_CONFIG_CACHE.clear()
        APP_CONFIG_CACHE.update(result)
        return result
    else:
        return APP_CONFIG_CACHE


def reload_config(yaml_file) -> dict:
    """重新加载配置"""
    return init_load_config(yaml_file, is_reload=True)


def get_config(config_key: str | SettingsKeyEnum, value_is_list: bool = False) -> Any | list[Any]:
    """
    获取配置
    :param config_key: 配置的键，如：app.name
    :param value_is_list: 是是否是列表
    :return: 配置的值
    """
    if value_is_list:
        return application_tools.get_settings_item_value_list(APP_CONFIG_CACHE, config_key)
    if isinstance(config_key, SettingsKeyEnum):
        config_key = config_key.value.name
    return APP_CONFIG_CACHE.get(config_key)
