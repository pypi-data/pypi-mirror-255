import json
import os.path
from typing import Any, Optional, Mapping, Sequence

from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import JSONResponse, FileResponse, Response, RedirectResponse

from afeng_tools.fastapi_tool import fastapi_settings
from afeng_tools.fastapi_tool.core.fastapi_enums import FastapiConfigKeyEnum
from afeng_tools.sqlalchemy_tools.tool import sqlalchemy_model_tools
from afeng_tools.sqlalchemy_tools.core.sqlalchemy_base_model import is_model_instance, is_model_class
from afeng_tools.web_tool import request_tools


def resp_404(message: str = '页面没找到！', request: Request = None, context_data: dict = None,
             app_code: str = 'common'):
    if request and not request_tools.is_json(request.headers):
        is_json_api = fastapi_settings.get_config(FastapiConfigKeyEnum.is_json_api)
        if is_json_api:
            return JSONResponse(
                status_code=404,
                content={"message": message, 'error_no': 404},
            )
        is_mobile = request_tools.is_mobile(request.headers.get('user-agent'))
        if context_data is None:
            context_data_func = fastapi_settings.get_config(FastapiConfigKeyEnum.error404_context_data_func)
            if context_data_func:
                context_data = context_data_func(message=message, is_mobile=is_mobile)
            else:
                context_data = {
                    "title": f'404错误页面',
                    'message': message
                }
        from afeng_tools.fastapi_tool.fastapi_jinja2_tools import create_template_response
        return create_template_response(request=request,
                                        template_file=f'{app_code}/' + (
                                            'mobile' if is_mobile else 'pc') + '/views/error/404.html',
                                        context=context_data)
    return JSONResponse(
        status_code=404,
        content={"message": message, 'error_no': 404},
    )


def resp_501(message: str, request: Request = None, context_data: dict = None, app_code: str = 'common'):
    if request and not request_tools.is_json(request.headers):
        is_json_api = fastapi_settings.get_config(FastapiConfigKeyEnum.is_json_api)
        if is_json_api:
            return JSONResponse(
                status_code=501,
                content={"message": message, 'error_no': 501},
            )
        is_mobile = request_tools.is_mobile(request.headers.get('user-agent'))
        if context_data is None:
            context_data_func = fastapi_settings.get_config(FastapiConfigKeyEnum.error501_context_data_func)
            if context_data_func:
                context_data = context_data_func(message=message, is_mobile=is_mobile)
            else:
                context_data = {
                    "title": f'操作失败页面',
                    'message': message
                }
        from afeng_tools.fastapi_tool.fastapi_jinja2_tools import create_template_response
        return create_template_response(request=request,
                                        template_file=f'{app_code}/' + (
                                            'mobile' if is_mobile else 'pc') + '/views/error/501.html',
                                        context=context_data)
    return JSONResponse(
        status_code=501,
        content={"message": message, 'error_no': 501},
    )


def resp_422(message: str | Sequence):
    return JSONResponse(
        status_code=422,
        content={"message": message, 'error_no': 422},
    )


def resp_500(message: str = '服务器内部错误！', request: Request = None, context_data: dict = None,
             app_code: str = 'common'):
    if request and not request_tools.is_json(request.headers):
        is_json_api = fastapi_settings.get_config(FastapiConfigKeyEnum.is_json_api)
        if is_json_api:
            return JSONResponse(
                status_code=500,
                content={"message": message, 'error_no': 500},
            )
        is_mobile = request_tools.is_mobile(request.headers.get('user-agent'))
        if context_data is None:
            context_data_func = fastapi_settings.get_config(FastapiConfigKeyEnum.error500_context_data_func)
            if context_data_func:
                context_data = context_data_func(message=message, is_mobile=is_mobile)
            else:
                context_data = {
                    "title": f'500错误页面',
                    'message': message
                }
        from afeng_tools.fastapi_tool.fastapi_jinja2_tools import create_template_response
        return create_template_response(request=request,
                                        template_file=f'{app_code}/' + (
                                            'mobile' if is_mobile else 'pc') + '/views/error/500.html',
                                        context=context_data)
    return JSONResponse(
        status_code=500,
        content={"message": message, 'error_no': 500},
    )


def resp_json(data: Any = None, error_no: int = 0, message: str = 'success'):
    if is_model_instance(data) or (data and isinstance(data, list) and len(data) > 0 and is_model_instance(data[0])):
        data = json.loads(sqlalchemy_model_tools.to_json(data))
    if isinstance(data, BaseModel):
        data = data.model_dump(mode='json')
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({"message": message, 'error_no': error_no, 'data': data}),
    )


def resp_file(file_path: str, file_name: str = None, download_flag: bool = False,
              context_data: dict = None) -> Response:
    """响应文件"""
    if not os.path.exists(file_path):
        return resp_404('资源不存在！', context_data=context_data)
    response = FileResponse(file_path)
    with open(file_path, "rb") as file:
        if download_flag:
            if file_name is None:
                file_name = os.path.split(file_path)[1]
            response.headers["Content-Disposition"] = f"attachment; filename={file_name}"
        response.body = file.read()
        return response


def redirect(target_url: str, status_code: int = 307,
             headers: Optional[Mapping[str, str]] = None,
             background: Optional[BackgroundTask] = None, ) -> RedirectResponse:
    """重定向"""
    return RedirectResponse(target_url, status_code=status_code, headers=headers, background=background)
