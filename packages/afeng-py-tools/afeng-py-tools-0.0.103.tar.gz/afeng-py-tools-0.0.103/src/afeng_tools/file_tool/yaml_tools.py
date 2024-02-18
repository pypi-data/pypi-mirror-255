"""
YAML工具: 安装 pip install pyyaml -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
"""
import yaml


def read_yaml(yaml_file: str, encoding: str = 'utf-8') -> dict:
    """读取yaml"""
    with open(yaml_file, 'r', encoding=encoding) as file:
        return yaml.load(file, Loader=yaml.FullLoader)
