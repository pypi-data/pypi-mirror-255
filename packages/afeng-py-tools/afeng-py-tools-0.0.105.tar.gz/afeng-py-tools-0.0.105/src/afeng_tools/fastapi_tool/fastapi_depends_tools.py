from enum import Enum
from typing import TypeVar, Type, Callable
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request

from afeng_tools.pydantic_tool.model.common_models import EnumItem


def convert_enum_type(param_name: str, enum_class: Type[Enum]) -> Callable:
    """
    转换枚举类型的装饰器， 使用示例：search_type: SearchTypeEnum = Depends(convert_enum_type('search_type', SearchTypeEnum)
    :param param_name: 参数名称
    :param enum_class: 枚举类型
    :return: 枚举
    """
    EnumType = TypeVar(enum_class.__name__, bound=enum_class)

    def convert_enum_type_wrapper(request: Request) -> EnumType:
        enum_type_str = request.query_params.get(param_name)
        if not enum_type_str:
            enum_type_str = request.path_params.get(param_name)
            if not enum_type_str:
                enum_type_str = request.form().get(param_name)
        type_enum_list = [tmp for tmp in enum_class if tmp.name == enum_type_str or tmp.value == enum_type_str]
        if type_enum_list:
            return type_enum_list[0]
        else:
            type_enum_list = [tmp for tmp in enum_class if
                              isinstance(tmp.value, EnumItem) and tmp.value.value == enum_type_str]
            if type_enum_list:
                return type_enum_list[0]
        raise RequestValidationError('请求参数[search_type]值有误！')

    return convert_enum_type_wrapper
