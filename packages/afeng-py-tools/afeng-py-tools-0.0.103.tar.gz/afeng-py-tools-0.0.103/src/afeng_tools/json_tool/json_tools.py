import datetime

import json
from array import array
from enum import Enum
from pydantic.json import pydantic_encoder
from _decimal import Decimal

from afeng_tools.pydantic_tool.model.common_models import EnumItem


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        elif isinstance(obj, int):
            return int(obj)
        elif isinstance(obj, float):
            return float(obj)
        elif isinstance(obj, array):
            return obj.tolist()
        elif isinstance(obj, Decimal):
            return str(obj)
        elif isinstance(obj, Enum):
            if isinstance(obj.value, str | int | float):
                return obj.value
            elif isinstance(obj.value, EnumItem):
                if obj.value.value is not None:
                    return obj.value.value
            return obj.name

        else:
            return super(JsonEncoder, self).default(obj)


def to_json(obj_data) -> str:
    """将Python中的对象转换为JSON中的字符串对象"""
    return json.dumps(obj_data, cls=JsonEncoder, ensure_ascii=False, indent=4)


def to_json_str(obj_data) -> str:
    """将Python中的对象转换为JSON中的字符串对象"""
    return json.dumps(obj_data, indent=4, ensure_ascii=False, default=pydantic_encoder)


def to_obj(str_data):
    """将JSON中的字符串对象转换为Python中的对象"""
    return json.loads(str_data)


def model_to_dict(model):
    """Model实例转dict"""
    model_dict = dict(model.__dict__)
    del model_dict['_sa_instance_state']
    return model_dict


def model_to_dict2(model):
    """单个对象转dict(效果等同上面的那个)"""
    return {c.name: getattr(model, c.name) for c in model.__table__.columns}


def model_to_json(model) -> str:
    """model或model集合转换为json字符串"""
    if isinstance(model, list):
        return to_json([model_to_dict2(tmp) for tmp in model])
    else:
        return to_json(model_to_dict(model))
