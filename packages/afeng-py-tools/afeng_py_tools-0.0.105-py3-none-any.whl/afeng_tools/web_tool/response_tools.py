"""
响应工具
"""
import json
from typing import Any

from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse, FileResponse, Response, RedirectResponse

from afeng_tools.web_tool.core.web_common_models import ResponseModel
from afeng_tools.sqlalchemy_tools.tool import sqlalchemy_model_tools
from afeng_tools.sqlalchemy_tools.core.sqlalchemy_base_model import is_model_instance, is_model_class


def create_json_response_data(data: Any = None, error_no: int = 0, message: str = 'success') -> ResponseModel:
    if is_model_instance(data) or (data and isinstance(data, list) and len(data) > 0 and is_model_instance(data[0])):
        data = json.loads(sqlalchemy_model_tools.to_json(data))
    if isinstance(data, BaseModel):
        data = data.model_dump(mode='json')
    return ResponseModel(
        error_no=error_no,
        message=message,
        data=jsonable_encoder(data)
    )


def create_json_response(response_model: ResponseModel) -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content=response_model.model_dump(mode='json')
    )


def json_response(data: Any = None, error_no: int = 0, message: str = 'success') -> JSONResponse:
    response_model = create_json_response_data(data=data, error_no=error_no, message=message)
    return create_json_response(response_model=response_model)


