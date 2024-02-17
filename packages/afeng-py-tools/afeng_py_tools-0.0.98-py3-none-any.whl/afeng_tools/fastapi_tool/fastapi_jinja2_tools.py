import os.path

from afeng_tools.web_tool import request_tools

from afeng_tools.encryption_tool import hashlib_tools
from starlette.responses import Response
from starlette.templating import Jinja2Templates, _TemplateResponse
from starlette.requests import Request

from afeng_tools.application_tool import settings_tools
from afeng_tools.application_tool.settings_enum import SettingsKeyEnum
from afeng_tools.file_tool import tmp_file_tools

jinja2_templates = Jinja2Templates(directory=settings_tools.get_config(SettingsKeyEnum.server_template_path))


def generate_unique_id(request: Request):
    return hashlib_tools.calc_unique_id(data_list=[
        request_tools.is_mobile(request.headers.get('user-agent')),
        request.method,
        request.url,
        request.query_params,
    ], split_chat='||')


def generate_request_cache_name(request: Request, cache_path: str):
    """
    生成request缓存
    :param request: request请求
    :param cache_path: 缓存路径
    :return:
    """
    unique_id = generate_unique_id(request)
    return os.path.join(cache_path, unique_id)


def create_template_response(request: Request, template_file: str, context: dict = None, is_cache=False,
                             cache_path: str = tmp_file_tools.get_user_tmp_dir()) -> _TemplateResponse:
    """
    创建模板响应
    :param request: Request
    :param template_file: 模板文件
    :param context: 上下文内容
    :param is_cache:
    :param cache_path:
    :return:
    """
    if isinstance(context, Response):
        return context
    if not context:
        context = dict()
    if 'request' not in context:
        context['request'] = request
    response = jinja2_templates.TemplateResponse(template_file, context=context)
    if is_cache:
        unique_id = generate_unique_id(request)
        with open(os.path.join(cache_path, f'{unique_id}.html'), 'wb') as f:
            f.write(response.body)
    return response
