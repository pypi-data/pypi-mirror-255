import enum
import os
from typing import Type, TypeVar, Callable

from fastapi import APIRouter, Body, Depends, Form
from starlette.requests import Request

from afeng_tools.fastapi_tool.admin.admin_router_model import AdminRouterModel
from afeng_tools.fastapi_tool.admin.admin_views_template import AdminViewsTemplate
from afeng_tools.jinja2_tool import jinja2_tools
from afeng_tools.pydantic_tool.pydantic_tools import create_model_by_po


def _create_json_proxy_func(source_func: Callable, orm_model_class: Type, add_flag: bool = False):
    """
    创建代理函数
    :param source_func: 需要被代理的函数
    :param orm_model_class: orm模型类
    :param add_flag: 是否是添加数据
    :return: 代理函数
    """
    ModelForm = TypeVar('ModelForm', bound=create_model_by_po(orm_model_class, add_flag=add_flag))

    async def proxy_func(request: Request, form_data: ModelForm = Body()):
        return await source_func(form_data, request=request)

    return proxy_func


def _create_form_proxy_old_func(source_func: Callable, orm_model_class: Type, add_flag: bool = False):
    """
    创建代理函数
    :param source_func: 需要被代理的函数
    :param orm_model_class: orm模型类
    :param add_flag: 是否是添加数据
    :return: 代理函数
    """
    model_class = create_model_by_po(orm_model_class, add_flag=add_flag)
    ModelForm = TypeVar('ModelForm', bound=model_class)

    async def convert_form_to_model(request: Request) -> ModelForm:
        form_data = await request.form()
        return model_class(**{tmp_key: tmp_value for tmp_key, tmp_value in form_data.items()})

    async def proxy_func(request: Request, form_data: ModelForm = Depends(convert_form_to_model)):
        return await source_func(form_data, request=request)

    return proxy_func


def _create_param_convert_depend_func(module_code: str, orm_model_class: Type) -> Callable:
    params_dict = {c.name: c for c in orm_model_class.__table__.columns}
    template_file = os.path.join(os.path.dirname(__file__), 'auto_covert_func.template')
    enum_import = []
    for tmp_value in params_dict.values():
        if issubclass(tmp_value.type.python_type, enum.Enum):
            enum_import.append(
                f"from {tmp_value.type.python_type.__module__} import {tmp_value.type.python_type.__name__}")
    params_list = []
    for tmp_field, tmp_column in params_dict.items():
        tmp_type = tmp_column.type.python_type
        if issubclass(tmp_type, list):
            tmp_item_type = tmp_column.type.item_type.python_type
            params_list.append(
                f"{tmp_field}: Optional[{tmp_column.type.python_type.__name__}[{tmp_item_type.__name__}]] = Form(title='{tmp_column.comment}', default=None)")
        else:
            if issubclass(tmp_type, enum.Enum):
                for tmp_enum in tmp_type:
                    tmp_type._value2member_map_[tmp_enum.name] = tmp_enum
            params_list.append(
                f"{tmp_field}: Optional[{tmp_column.type.python_type.__name__}] = Form(title='{tmp_column.comment}', default=None)")

    args_list = [f"'{tmp}': {tmp}" for tmp in params_dict.keys()]
    template_content = jinja2_tools.format_template(template_file, context={
        'module_code': module_code,
        'enum_import_str': '\n'.join(enum_import),
        'params_str': ', '.join(params_list),
        'args_str': '{' + (', '.join(args_list)) + '}'
    })
    exec(template_content)
    return eval(f'convert_form_to_{module_code}_model_func')


def _create_form_proxy_func(module_code: str, source_func: Callable, orm_model_class: Type, add_flag: bool = False):
    """
    创建代理函数
    :param source_func: 需要被代理的函数
    :param orm_model_class: orm模型类
    :param add_flag: 是否是添加数据
    :return: 代理函数
    """
    model_class = create_model_by_po(orm_model_class, add_flag=add_flag)
    param_convert_depend_func = _create_param_convert_depend_func(module_code=module_code,
                                                                  orm_model_class=orm_model_class)

    async def proxy_func(request: Request,
                         form_data: dict = Depends(param_convert_depend_func)):
        old_form_data = await request.form()
        if old_form_data:
            array_field_dict = dict()
            for tmp_key in old_form_data.keys():
                if tmp_key.endswith('[]'):
                    tmp_new_key = tmp_key.removesuffix('[]')
                    if not array_field_dict.get(tmp_new_key):
                        array_field_dict[tmp_new_key] = old_form_data.getlist(tmp_key)
            form_data.update(array_field_dict)
        return await source_func(request, model_class(**form_data))

    return proxy_func


def create_admin_router(admin_router_model: AdminRouterModel) -> tuple[APIRouter, APIRouter]:
    """
    添加管理路由
    :param admin_router_model:
    :return: 管理页面路由，管理api路由
    """
    module_code: str = admin_router_model.module_code
    orm_model_class = admin_router_model.orm_model_class
    admin_views_template: AdminViewsTemplate = admin_router_model.admin_views_template
    method_dict = dict()
    if len(type(admin_views_template).__mro__) > 2 and type(admin_views_template).__mro__[1] == AdminViewsTemplate:
        method_dict = [tmp for tmp in type(admin_views_template).__dict__.keys()]
        method_dict.remove('__module__')
        method_dict.remove('__doc__')
    page_router = APIRouter(prefix=f'/admin/{module_code}', tags=[f'管理-{tmp}' for tmp in admin_router_model.tag_list])
    page_router.get('')(admin_views_template.index_page)
    page_router.get('/index')(admin_views_template.index_page)
    page_router.get('/home')(admin_views_template.index_page)
    page_router.get('/add')(admin_views_template.add_page)
    page_router.get('/update/{id_value}')(admin_views_template.update_page)
    page_router.get('/show')(admin_views_template.show_page)

    api_router = APIRouter(prefix=f'/admin/api/{module_code}',
                           tags=[f'管理Api-{tmp}' for tmp in admin_router_model.tag_list])
    if 'add_data' in method_dict:
        api_router.post('/add')(admin_views_template.add_data)
    else:
        api_router.post('/add')(
            _create_form_proxy_func(module_code, admin_views_template.add_data, orm_model_class, add_flag=True))
    if 'update_data' in method_dict:
        api_router.post('/update')(admin_views_template.update_data)
    else:
        api_router.post('/update')(
            _create_form_proxy_func(module_code, admin_views_template.update_data, orm_model_class))
    api_router.get('/get/{id_value}')(admin_views_template.get_data)
    api_router.post('/delete/{id_value}')(admin_views_template.delete_data)
    api_router.post('/more_delete')(admin_views_template.more_delete_data)
    api_router.get('/list')(admin_views_template.list_data)
    return page_router, api_router
