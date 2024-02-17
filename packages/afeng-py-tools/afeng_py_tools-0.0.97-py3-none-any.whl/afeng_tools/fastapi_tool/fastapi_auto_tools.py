import importlib
import os
from enum import Enum

from afeng_tools.application_tool.application_models import AppInfo
from afeng_tools.pydantic_tool.model.common_models import EnumItem


def auto_load_apps(root_path: str, root_name: str = 'apps',
                   app_info_name: str = 'app_info') -> dict[str, AppInfo]:
    """自动加载apps.{app_name}模块中的app_info"""
    app_dict = dict()
    for tmp_app_name in os.listdir(root_path):
        if tmp_app_name.startswith('__'):
            continue
        if os.path.isdir(os.path.join(root_path, tmp_app_name)):
            tmp_app = importlib.import_module(f'{root_name}.{tmp_app_name}')
            tmp_app_info = tmp_app.__getattribute__(app_info_name)
            if tmp_app_info:
                app_dict[tmp_app_info.code] = tmp_app_info
    return app_dict


def auto_set_enum_item_value(local_variable: dict):
    """自动设置Enum中EnumItem的value"""
    for tmp_key in {tmp for tmp in local_variable.keys() if tmp.endswith('Enum')}:
        tmp_value = local_variable.get(tmp_key)
        if isinstance(tmp_value, type) and issubclass(tmp_value, Enum):
            for tmp_enum in tmp_value:
                if isinstance(tmp_enum.value, EnumItem) and tmp_enum.value.value is None:
                    tmp_enum.value.value = tmp_enum.name
