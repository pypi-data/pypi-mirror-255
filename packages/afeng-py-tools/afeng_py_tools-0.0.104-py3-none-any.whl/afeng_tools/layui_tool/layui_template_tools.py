"""
LayUI工具
- pip install pydantic -i https://pypi.tuna.tsinghua.edu.cn/simple/
- pip install Jinja2 -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
"""

import os.path
from typing import Callable

from afeng_tools.jinja2_tool import jinja2_tools
from afeng_tools.layui_tool.core.layui_models import LayUiFormItem, LayUiTableCol, LayUiTableData, LayUiTableActionItem, \
    LayUiFormStep

template_env = jinja2_tools.create_template_env([os.path.join(os.path.dirname(__file__), 'template')])


def table_data_parse(data_list: list, parse_callback: Callable[[list], LayUiTableData]) -> LayUiTableData:
    """表单数据转换"""
    return parse_callback(data_list)


def render_step_form_template(title: str, form_step_list: list[LayUiFormStep], height: int = 500,
                              file_upload_url: str = '/admin/resource/upload') -> str:
    return jinja2_tools.format_template('form/step_form.html', context={
        'title': title,
        'height': height,
        'form_step_list': form_step_list,
        'file_upload_url': file_upload_url
    }, env=template_env)


def render_add_template(title: str, form_item_list: list[LayUiFormItem], add_url: str,
                        has_parent: bool = True, finish_redirect_url: str = None,
                        file_upload_url: str = '/admin/resource/upload') -> str:
    return jinja2_tools.format_template('table/add.html', context={
        'title': title,
        'item_list': form_item_list,
        'add_url': add_url,
        'has_parent': has_parent,
        'finish_redirect_url': finish_redirect_url,
        'file_upload_url': file_upload_url
    }, env=template_env)


def render_edit_template(title: str, form_item_list: list[LayUiFormItem], edit_url: str,
                         file_upload_url: str = '/admin/resource/upload') -> str:
    return jinja2_tools.format_template('table/edit.html', context={
        'title': title,
        'item_list': form_item_list,
        'edit_url': edit_url,
        'file_upload_url': file_upload_url
    }, env=template_env)


def render_show_template(title: str, form_item_list: list[LayUiFormItem]) -> str:
    return jinja2_tools.format_template('table/show.html', context={
        'title': title,
        'item_list': form_item_list,
    }, env=template_env)


def render_table_template(title: str, search_form_item_list: list[LayUiFormItem], data_url: str,
                          col_list: list[LayUiTableCol],
                          page_name: str = 'page', limit_name: str = 'limit',
                          search_params_name: str = 'searchParams',
                          add: bool = False, add_html_url: str = 'add',
                          edit: bool = False, edit_html_url: str = 'edit',
                          delete: bool = False, delete_url: str = None, delete_field: str = 'id',
                          more_delete: bool = False, more_delete_url: str = None, more_delete_name: str = 'ids',
                          more_delete_field: str = 'id',
                          action_list: list[LayUiTableActionItem] = None,
                          message: str = None) -> str:
    """
    渲染表格模板
    :param title:
    :param search_form_item_list:
    :param data_url:
    :param col_list:
    :param page_name: 页码的参数名称，默认：page
    :param limit_name: 每页数据量的参数名，默认：limit
    :param search_params_name:
    :param add:
    :param add_html_url:
    :param edit:
    :param edit_html_url:
    :param delete:
    :param delete_url:
    :param delete_field:
    :param more_delete: 是否开启多条删除
    :param more_delete_url: 多条删除url
    :param more_delete_name: 多条删除name
    :param more_delete_field: 多条删除字段名
    :param action_list: 操作列表
    :param message:
    :return:
    """
    return jinja2_tools.format_template('table/list.html', context={
        'title': title,
        'search_form_item_list': search_form_item_list,
        'data_url': data_url,
        'col_list': col_list,
        'page_name': page_name,
        'limit_name': limit_name,
        'search_params_name': search_params_name,
        'add': add,
        'add_html_url': add_html_url,
        'edit': edit,
        'edit_html_url': edit_html_url,
        'delete': delete,
        'delete_url': delete_url,
        'delete_field': delete_field,
        'more_delete': more_delete,
        'more_delete_url': more_delete_url,
        'more_delete_name': more_delete_name,
        'more_delete_field': more_delete_field,
        'action_list': action_list,
        'message': message
    }, env=template_env)


if __name__ == '__main__':
    print(render_table_template('测试列表', search_form_item_list=[
        LayUiFormItem(title='书名', name='title'),
        LayUiFormItem(title='isbn', name='isbn')
    ], data_url='../api/table.json', col_list=[
        LayUiTableCol(field='id', title='主键'),
        LayUiTableCol(field='city', title='城市'),
        LayUiTableCol(field='sign', title='签名'),
        LayUiTableCol(field='experience', title='积分'),
    ]))
