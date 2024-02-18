"""
FastAPI路由工具
"""
import importlib
import os

from fastapi import APIRouter
from starlette.routing import BaseRoute

from afeng_tools.application_tool.application_models import AppInfo


def create_router(prefix: str, tags: list[str], router_list: list[BaseRoute] = None) -> APIRouter:
    """创建路由"""
    if router_list:
        router = APIRouter(prefix=prefix, tags=tags, routes=router_list)
    else:
        router = APIRouter(prefix=prefix, tags=tags)
    return router


def router_add_prefix(prefix: str, router_list: list[APIRouter | BaseRoute]):
    """路由添加前缀"""
    result_router_list = []
    if prefix:
        for tmp_router in router_list:
            tmp_router.prefix = f'{prefix}{tmp_router.prefix}'
            if tmp_router.routes:
                for child_router in tmp_router.routes:
                    child_router.path = f'{prefix}{child_router.path}'
            result_router_list.append(tmp_router)
    return result_router_list


def auto_load_routers(web_root_path: str, web_root_name: str = None,
                      view_file_name: str = 'views', router_name='router') -> list[APIRouter | BaseRoute]:
    """自动加载web.{app}.views文件中的路由"""
    router_list = []
    if web_root_name is None:
        web_root_name = os.path.split(web_root_path)[1]
    if os.path.exists(web_root_path):
        for app_name in os.listdir(web_root_path):
            if os.path.isdir(
                    os.path.join(web_root_path, app_name)) and app_name != '__pycache__' and app_name != 'admin':
                if os.path.exists(os.path.join(web_root_path, app_name, view_file_name + '.py')):
                    web_app_views = importlib.import_module(f'{web_root_name}.{app_name}.{view_file_name}')
                    router_list.append(web_app_views.__getattribute__(router_name))
    return router_list


def auto_load_apps_router(app_info_dict: dict[str, AppInfo], apps_prefix: str = 'apps', web_path_name: str = 'web') -> list[APIRouter | BaseRoute]:
    """自动加载apps下app的router"""
    router_list = []
    for tmp_code, tmp_app_info in app_info_dict.items():
        router_list.extend(router_add_prefix(prefix=tmp_app_info.prefix,
                                             router_list=auto_load_routers(tmp_app_info.web_path,
                                                                           web_root_name=f'{apps_prefix}.{tmp_code}.{web_path_name}')))
    return router_list
