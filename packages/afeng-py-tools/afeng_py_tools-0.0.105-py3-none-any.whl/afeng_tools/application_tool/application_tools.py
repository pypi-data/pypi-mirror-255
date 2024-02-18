import os
from pathlib import Path
from typing import Any

from afeng_tools.application_tool.settings_enum import SettingsKeyEnum
from afeng_tools.file_tool import yaml_tools


def get_settings_item_value_list(yaml_config: dict, settings_key: str | SettingsKeyEnum) -> list[Any]:
    """获取某个配置项的值列表"""
    item_key = settings_key
    if isinstance(settings_key, SettingsKeyEnum):
        item_key = settings_key.value.name
    if yaml_config.get(item_key):
        item_value = yaml_config.get(item_key)
        item_value_list = []
        if isinstance(item_value, list):
            item_value_list = item_value
        else:
            if isinstance(item_value, str) and ',' in item_value:
                item_value_list = item_value.split(',')
            else:
                item_value_list.append(item_value)
        return item_value_list


def _tree_read_config(config: dict, prefix_key: str = None):
    """
    递归读取配置
    :param config: 配置字典
    :param prefix_key: 前缀键
    :return:
    """
    result = dict()
    if config and isinstance(config, dict):
        for tmp_key in config.keys():
            key = prefix_key + '.' + tmp_key if prefix_key else tmp_key
            value = config.get(tmp_key)
            if value and isinstance(value, dict):
                child_result = _tree_read_config(value, key)
                result.update(child_result)
            else:
                result[key] = value
    return result


def read_application_config(yaml_file) -> dict[str, Any]:
    """
    读取application配置
    :param yaml_file: yaml配置文件
    :return: 返回配置字典，如：app.name
    """
    yaml_config = yaml_tools.read_yaml(yaml_file)
    return _tree_read_config(yaml_config)


def read_all_config(yaml_file) -> dict[str, Any]:
    """
    读取所有的配置
    :param yaml_file: yaml配置文件
    :return: 返回配置字典，如：app.name
    """
    yaml_config = read_application_config(yaml_file)
    active_list = get_settings_item_value_list(yaml_config, SettingsKeyEnum.app_active)
    if active_list:
        for tmp_active in active_list:
            active_file_name = f'{os.path.split(yaml_file)[1].rsplit(".", maxsplit=1)[0]}-{tmp_active}{os.path.splitext(yaml_file)[1]}'
            yaml_config.update(read_application_config(os.path.join(Path(yaml_file).parent, active_file_name)))
    return yaml_config
