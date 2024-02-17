"""
- pip install Jinja2 -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
"""
import os

from jinja2 import Template, FileSystemLoader, Environment

from afeng_tools.decorator_tool import decorator_tools
from afeng_tools.jinja2_tool import jinja2_filters


def _auto_append_filter(env: Environment):
    """自动添加过滤器"""
    func_members = decorator_tools.get_func_by_decorator(jinja2_filters, 'jinja2_filter')
    if func_members:
        for tmp_member in func_members.values():
            env.filters[getattr(tmp_member, '__filter_name__')] = tmp_member
    return env


def create_template(content_list: list[str]) -> Template:
    """创建模板"""
    return Template('\n'.join(content_list))


def create_template_env(directory_list: list[str], auto_escape: bool = True) -> Environment:
    """获取模板环境"""
    result_env = Environment(loader=FileSystemLoader(directory_list),
                             autoescape=auto_escape)
    result_env = _auto_append_filter(result_env)
    return result_env


def format_template(template_file: str, context: dict = None, env: Environment = None,
                    template_path: str = None) -> str:
    """格式化模板"""
    if env is None:
        if template_path is None:
            template_path = os.path.dirname(template_file)
            template_file = os.path.split(template_file)[1]
        env = create_template_env([template_path])
    template = env.get_template(template_file)
    return template.render(**context)


def render_template(template: Template, context: dict = None):
    """格式Template"""
    return template.render(**context)


if __name__ == '__main__':
    print()
