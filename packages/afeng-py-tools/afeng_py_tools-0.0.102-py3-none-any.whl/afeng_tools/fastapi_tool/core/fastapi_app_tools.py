"""
Fast API App工具集
"""
import asyncio
import traceback
from typing import Callable

from fastapi import FastAPI, APIRouter
from fastapi.exceptions import RequestValidationError
from fastapi.logger import logger
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.requests import Request

from starlette.staticfiles import StaticFiles

from afeng_tools.application_tool import settings_tools
from afeng_tools.application_tool.settings_enum import SettingsStaticItem, SettingsKeyEnum
from afeng_tools.fastapi_tool import fastapi_response_tools, fastapi_settings
from afeng_tools.fastapi_tool.core.fastapi_enums import FastapiConfigKeyEnum


def _register_cors(app: FastAPI):
    """跨域设置"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def _register_router(app: FastAPI, router_list: list[APIRouter] = None, router_dict: dict[str, APIRouter] = None):
    """注册路由"""
    # 注册router
    if router_list:
        for tmp_router in router_list:
            app.include_router(tmp_router)
    if router_dict:
        for tmp_prefix, tmp_router in router_dict.items():
            app.include_router(tmp_router, prefix=tmp_prefix)


def _register_exception_handler(app: FastAPI):
    """注册捕获全局异常"""

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        请求参数验证异常
        :param request: 请求头信息
        :param exc: 异常对象
        :return:
        """
        # 日志记录异常详细上下文
        logger.error(
            f"全局异常: \n{request.method}URL{request.url}\nHeaders:{request.headers}\n{traceback.format_exc()}")
        return fastapi_response_tools.resp_404(message="请求参数未找到！", request=request)

    @app.exception_handler(Exception)
    async def all_exception_handler(request: Request, exc: Exception):
        """
        全局所有异常
        :param request:
        :param exc:
        :return:
        """
        background_work_func = fastapi_settings.get_config(FastapiConfigKeyEnum.error500_background_work_func)
        traceback_msg = traceback.format_exc()
        if background_work_func and isinstance(background_work_func, Callable):
            asyncio.ensure_future(background_work_func(request, exc, traceback_msg))
        logger.error(
            f"全局异常: \n{request.method}URL:{request.url}\nHeaders:{request.headers}\n{traceback_msg}", exc)
        return fastapi_response_tools.resp_500(message="服务器内部错误", request=request)


def _register_middleware(app: FastAPI):
    """注册中间件"""
    # minimum_size：需要 GZip 响应的最小大小（以字节为单位）。默认值为 500。
    app.add_middleware(GZipMiddleware, minimum_size=1000)


def _register_static_file(app: FastAPI):
    """注册静态文件"""
    # 静态文件
    app_static_value = settings_tools.get_config(SettingsKeyEnum.server_static)
    if isinstance(app_static_value, list):
        for i, tmp_static in enumerate(app_static_value):
            if isinstance(tmp_static, SettingsStaticItem):
                app.mount(path=tmp_static.url,
                          app=StaticFiles(directory=tmp_static.path, html=True),
                          name=tmp_static.name if tmp_static.name else f'static_{i}')
    else:
        if isinstance(app_static_value, SettingsStaticItem):
            app.mount(path=app_static_value.url,
                      app=StaticFiles(directory=app_static_value.path, html=True),
                      name=app_static_value.name if app_static_value.name else f'static')


def create_app(router_list: list[APIRouter] = None, router_dict: dict[str, APIRouter] = None):
    """创建FastAPI应用"""
    is_debug = settings_tools.get_config(SettingsKeyEnum.app_is_debug)
    app = FastAPI(debug=is_debug, openapi_url=None, docs_url=None, redoc_url=None)
    # 注册路由
    _register_router(app, router_list=router_list, router_dict=router_dict)
    # 注册捕获全局异常
    _register_exception_handler(app)
    # 注册中间件（请求拦截）
    _register_middleware(app)
    # 跨域设置
    _register_cors(app)
    # 注册静态资源
    _register_static_file(app)
    return app
