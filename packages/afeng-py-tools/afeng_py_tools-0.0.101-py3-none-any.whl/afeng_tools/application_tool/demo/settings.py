"""
项目配置
"""
import os
from pathlib import Path

from afeng_tools.application_tool import settings_tools

# 项目根路径
ROOT_PATH = Path(__file__).parent.parent.parent.absolute()
# 本地资源文件路径
RESOURCE_PATH = os.path.join(ROOT_PATH, 'resource')
# application.yaml配置路径
application_yaml = os.path.join(ROOT_PATH, 'src/config/application.yml')
# 初始化配置参数
settings_tools.init_config_param(root=ROOT_PATH, resource=RESOURCE_PATH)
# 初始化配置
settings_tools.init_load_config(application_yaml)

if __name__ == '__main__':
    print(settings_tools.get_config('app.active'))
    # print(settings_tools.reload_config(os.path.join(ROOT_PATH, 'src/tool/application/yaml_demo/application.yml')))
    print(settings_tools.APP_CONFIG_CACHE)