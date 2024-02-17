from typing import Type

from pydantic import BaseModel
from starlette.datastructures import FormData
from starlette.requests import Request

from afeng_tools.convert_tool.type_convert_tools import convert_value_to_type


def form_params_convert_to_model(form_model_class: Type[BaseModel]):
    """将表单参数转换为pydantic的Model对象"""
    async def func_wrap(request: Request):
        body = await request.form()
        if body:
            model_value_dict = dict()
            field_dict = form_model_class.model_fields
            for tmp_key, tmp_value in body.items():
                if tmp_key in field_dict:
                    model_value_dict[tmp_key] = convert_value_to_type(tmp_value, field_dict.get(tmp_key).annotation)
            return form_model_class(**model_value_dict)
    return func_wrap


async def do_handle_form_array_item(form_data: FormData) -> FormData:
    """处理form表单提交的数组"""
    new_form_data_list = []
    for tmp_key in form_data.keys():
        if tmp_key.endswith('[]'):
            new_form_data_list.append((tmp_key.removesuffix('[]'), form_data.getlist(tmp_key)))
        else:
            new_form_data_list.append((tmp_key, form_data.get(tmp_key)))
    return FormData(new_form_data_list)
