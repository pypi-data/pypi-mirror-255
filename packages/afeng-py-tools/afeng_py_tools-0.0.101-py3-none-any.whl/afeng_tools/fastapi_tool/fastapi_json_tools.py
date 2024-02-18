"""
fastapi的json工具类
"""
import json
from typing import Any
from fastapi.encoders import jsonable_encoder


def to_json_str(obj_data: Any, indent: int = None, allow_nan: bool = False) -> str:
    """转换为json字符串"""
    return json.dumps(
        jsonable_encoder(obj_data),
        ensure_ascii=False,
        allow_nan=allow_nan,
        indent=indent,
        separators=(",", ":"),
    )


def to_json_bytes(obj_data: Any, indent: int = None, allow_nan: bool = False) -> bytes:
    """转换为json字节"""
    return to_json_str(obj_data, allow_nan=allow_nan, indent=indent).encode("utf-8")
