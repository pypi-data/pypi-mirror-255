import openapi_client
from openapi_client.api import auth_api, userinfo_api, multimediafile_api, filemanager_api, fileinfo_api, fileupload_api
from afeng_tools.decorator_tool.decorator_tools import run_func


def auto_api_client(func):
    """自动导入 api_client:ApiClient"""
    def wrap(*args, **kwargs):
        if 'api_client' in kwargs:
            return run_func(func, *args, **kwargs)
        with openapi_client.ApiClient() as api_client:
            kwargs['api_client'] = api_client
            return run_func(func, *args, **kwargs)
    return wrap


def auto_auth_api(func):
    """自动导入 api_instance:AuthApi"""
    def wrap(*args, **kwargs):
        if 'api_instance' in kwargs:
            return run_func(func, *args, **kwargs)
        with openapi_client.ApiClient() as api_client:
            api_instance = auth_api.AuthApi(api_client)
            kwargs['api_instance'] = api_instance
            return run_func(func, *args, **kwargs)
    return wrap


def auto_userinfo_api(func):
    """自动导入 api_instance:UserinfoApi"""
    def wrap(*args, **kwargs):
        if 'api_instance' in kwargs:
            return run_func(func, *args, **kwargs)
        with openapi_client.ApiClient() as api_client:
            api_instance = userinfo_api.UserinfoApi(api_client)
            kwargs['api_instance'] = api_instance
            return run_func(func, *args, **kwargs)
    return wrap


def auto_fileinfo_api(func):
    """自动导入 api_instance:FileinfoApi"""
    def wrap(*args, **kwargs):
        if 'api_instance' in kwargs:
            return run_func(func, *args, **kwargs)
        with openapi_client.ApiClient() as api_client:
            api_instance = fileinfo_api.FileinfoApi(api_client)
            kwargs['api_instance'] = api_instance
            return run_func(func, *args, **kwargs)
    return wrap


def auto_media_file_api(func):
    """自动导入 api_instance:MultimediafileApi"""
    def wrap(*args, **kwargs):
        if 'api_instance' in kwargs:
            return run_func(func, *args, **kwargs)
        with openapi_client.ApiClient() as api_client:
            api_instance = multimediafile_api.MultimediafileApi(api_client)
            kwargs['api_instance'] = api_instance
            return run_func(func, *args, **kwargs)
    return wrap


def auto_file_manager_api(func):
    """自动导入 api_instance:FilemanagerApi"""
    def wrap(*args, **kwargs):
        if 'api_instance' in kwargs:
            return run_func(func, *args, **kwargs)
        with openapi_client.ApiClient() as api_client:
            api_instance = filemanager_api.FilemanagerApi(api_client)
            kwargs['api_instance'] = api_instance
            return run_func(func, *args, **kwargs)
    return wrap


def auto_file_upload_api(func):
    """自动导入 api_instance:FileuploadApi"""
    def wrap(*args, **kwargs):
        if 'api_instance' in kwargs:
            return run_func(func, *args, **kwargs)
        with openapi_client.ApiClient() as api_client:
            api_instance = fileupload_api.FileuploadApi(api_client)
            kwargs['api_instance'] = api_instance
            return run_func(func, *args, **kwargs)
    return wrap


