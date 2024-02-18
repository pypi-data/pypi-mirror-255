"""
百度盘工具
"""
import json
import os.path
import re
from datetime import datetime

from afeng_tools.baidu_pan_tool import baidu_pan_settings
from afeng_tools.baidu_pan_tool.baidu_pan_enum import BaidupanConfigKeyEnum
from afeng_tools.baidu_pan_tool.core.baidu_pan_models import TokenInfo, MultimediaFileInfo, UploadCreateResult
from afeng_tools.baidu_pan_tool.tools import file_path_tools, file_upload_tools
from afeng_tools.encryption_tool import hashlib_tools
from afeng_tools.file_tool import file_tools, tmp_file_tools
from afeng_tools.http_tool import http_download_tools
from afeng_tools.log_tool.loguru_tools import get_logger, log_error

logger = get_logger()

try:
    from afeng_tools.baidu_pan_tool.tools import auth_tools
except ModuleNotFoundError:
    from afeng_tools.baidu_pan_tool.tools import auth_web_tools as auth_tools


def _save_token(token_info: TokenInfo):
    """保存token到本地"""
    file_tools.save_file(json.dumps(token_info.model_dump(mode='json')).encode('utf-8'),
                         baidu_pan_settings.get_config(BaidupanConfigKeyEnum.token_file), binary_flag=True)


def _is_need_refresh(token_info: TokenInfo):
    """
    判断token是否需要刷新
    :param token_info:
    :return: 是否需要刷新，默认是False
    """
    space_time = datetime.now() - token_info.token_time
    space_seconds = space_time.total_seconds()
    if space_seconds - token_info.expires_in > 3600:
        return True
    return False


def get_access_token() -> str:
    """获取Access Token"""
    if os.path.exists(baidu_pan_settings.get_config(BaidupanConfigKeyEnum.token_file)):
        # token文件转换为token
        token_info_bytes = file_tools.read_file(baidu_pan_settings.get_config(BaidupanConfigKeyEnum.token_file),
                                                binary_flag=True)
        token_info = TokenInfo.model_validate_json(token_info_bytes)
        # 判断已有的token是否需要刷新
        if _is_need_refresh(token_info):
            # 1、刷新token
            token_info = auth_tools.refresh_token(token_info.refresh_token,
                                                  baidu_pan_settings.get_config(BaidupanConfigKeyEnum.app_key),
                                                  baidu_pan_settings.get_config(BaidupanConfigKeyEnum.secret_key))
            # 2、保存刷新后的token
            _save_token(token_info)
        return token_info.access_token
    else:
        # 获取授权码Code
        auth_code = auth_tools.get_authorization_code(
            app_id=baidu_pan_settings.get_config(BaidupanConfigKeyEnum.app_id),
            app_key=baidu_pan_settings.get_config(BaidupanConfigKeyEnum.app_key))
        # 换取AccessToken凭证
        token_info = auth_tools.get_token_authorization_code(auth_code=auth_code,
                                                             app_key=baidu_pan_settings.get_config(
                                                                 BaidupanConfigKeyEnum.app_key),
                                                             secret_key=baidu_pan_settings.get_config(
                                                                 BaidupanConfigKeyEnum.secret_key))
        # 保存token到本地
        _save_token(token_info)
        return token_info.access_token


def list_file(access_token: str, dir_path: str = '/', order: str = 'name', desc: int = 0,
              start: int = 0, limit: int = 100, web: int = 0, folder: int = 0,
              show_empty: int = 1) -> MultimediaFileInfo:
    """
    获取文件列表: 本接口用于获取用户网盘中指定目录下的文件列表。返回的文件列表支持排序、分页等操作。
    :param access_token: Access Token
    :param dir_path: 需要list的目录，以/开头的绝对路径, 默认为/
    :param order: 排序字段：默认为name；
                time表示先按文件类型排序，后按修改时间排序；
                name表示先按文件类型排序，后按文件名称排序；(注意，此处排序是按字符串排序的)
                size表示先按文件类型排序，后按文件大小排序。
    :param desc: 默认为升序，设置为1实现降序, 排序的对象是当前目录下所有文件，不是当前分页下的文件
    :param start: 起始位置，从0开始
    :param limit: 查询数目，默认为1000，建议最大不超过1000
    :param web: 值为1时，返回dir_empty属性和缩略图数据
    :param folder: 是否只返回文件夹，0 返回所有，1 只返回文件夹，且属性只返回path字段
    :param show_empty: 是否返回dir_empty属性，0 不返回，1 返回
    :return:
    """
    return file_path_tools.list_all_by_page(access_token=access_token, dir_path=dir_path,
                                            order=order, desc=desc, start=start, limit=limit,
                                            web=web, folder=folder, show_empty=show_empty)


def get_share_url(share_msg: str) -> str | None:
    """
    提取分享信息中的分享链接
    :param share_msg: 分享信息，如： 链接:https://pan.baidu.com/s/1NnNRMgCdzQbBFXtx_xGezg 提取码:2112
    :return: 分享链接，如：https://pan.baidu.com/s/1NnNRMgCdzQbBFXtx_xGezg?pwd=2112
    """
    url_re_search = re.search('(https://pan\.baidu\.com/s/[\w-]*)', share_msg)
    if url_re_search is None:
        url_re_search = re.search('(https://pan\.baidu\.com/share/[/?=&\w-]*)', share_msg)
    if url_re_search is None:
        return
    share_url = url_re_search.group(1)
    if 'pwd=' in share_url:
        return share_url
    pwd_re_search = re.search('提取码:(\w{4})', share_msg)
    if pwd_re_search:
        share_pwd = pwd_re_search.group(1)
        return share_url + '?pwd=' + share_pwd
    return share_url


def save_to_pan(file_url: str, pan_path: str, include_filename: bool = False) -> UploadCreateResult:
    """
    保存到网盘
    :param file_url: 文件的url
    :param pan_path: 网盘存储的目录
    :param include_filename: 路径是否包含文件名
    :return: 存储结果
    """
    access_token = get_access_token()
    tmp_path = tmp_file_tools.get_user_tmp_dir()
    tmp_file_name = file_url.rsplit('/', maxsplit=1)[-1].split('?', maxsplit=1)[0]
    tmp_file = os.path.join(tmp_path, tmp_file_name)
    try:
        http_download_tools.download_chunk_file(download_url=file_url,
                                                save_path=tmp_path,
                                                save_file_name=tmp_file_name)
        if not include_filename:
            tmp_pan_file_name = hashlib_tools.calc_file_md5(tmp_file) + '.' + tmp_file_name.rsplit('.')[1]
            pan_path = f'{pan_path}/{tmp_pan_file_name}'
        return file_upload_tools.upload_file(access_token, local_file=tmp_file, pan_path=pan_path, rtype=3)
    except Exception as e:
        log_error(logger, f'[百度网盘]下载文件[{file_url}], 保存文件到百度网盘[{pan_path}]出现异常', e)
    finally:
        if os.path.exists(tmp_file):
            os.remove(tmp_file)


def upload_to_pan(local_file: str, pan_path: str, include_filename: bool = False) -> UploadCreateResult:
    """
    保存到网盘
    :param local_file: 本地文件
    :param pan_path: 网盘存储的目录
    :param include_filename: 路径是否包含文件名
    :return: 存储结果
    """
    error_chars = '?|"><:*'
    for tmp in error_chars:
        pan_path = pan_path.replace(tmp, '_')
    access_token = get_access_token()
    tmp_file_name = local_file.rsplit('/', maxsplit=1)[-1].split('?', maxsplit=1)[0]
    try:
        if not include_filename:
            tmp_pan_file_name = hashlib_tools.calc_md5(local_file) + '.' + tmp_file_name.rsplit('.')[1]
            pan_path = f'{pan_path}/{tmp_pan_file_name}'
        return file_upload_tools.upload_file(access_token, local_file=local_file, pan_path=pan_path, rtype=3)
    except Exception as e:
        log_error(logger, f'[百度网盘]文件[{local_file}], 保存文件到百度网盘[{pan_path}]出现异常', e)
