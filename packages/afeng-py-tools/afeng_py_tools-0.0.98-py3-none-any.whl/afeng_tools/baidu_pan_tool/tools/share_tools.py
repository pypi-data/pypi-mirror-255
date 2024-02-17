"""
分享工具(付费接口)
"""
import json

import requests

from afeng_tools.baidu_pan_tool.core.baidu_pan_models import CreateShareResult, VerifySharePwdResult, QueryShareInfoResult, \
    QueryShareDataListResult, TransferShareResult, TransferShareTaskQueryResult
from afeng_tools.http_tool import http_params_tools
from afeng_tools.log_tool.loguru_tools import log_error, get_logger

logger = get_logger()


def create_share(app_id: str, access_token: str, fs_id_list: list[str], pwd: str,
                 period: int = 7, remark: str = None) -> CreateShareResult:
    """
    创建分享链接
    :param app_id: 	应用ID
    :param access_token: Access Token
    :param fs_id_list: 分享文件id列表，json格式，字符串数组
    :param pwd: 分享密码，长度4位，数字+小写字母组成
    :param period: 分享有效期，单位天
    :param remark: 分享备注
    :return: CreateShareResult
    """
    params = {
        'product': 'netdisk',
        'appid': app_id,
        'access_token': access_token
    }
    form_data = {
        'fsid_list': json.dumps(fs_id_list),
        'period': str(period),
        'pwd': pwd,
        'remark': remark
    }
    headers = {
        'Host': 'pan.baidu.com'
    }
    try:
        post_url = 'https://pan.baidu.com/apaas/1.0/share/set?' + http_params_tools.url_encode_params(params)
        print(post_url)
        response = requests.post(post_url, data=form_data, headers=headers)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            api_response = response.json()
            if api_response['errno'] == 0:
                return CreateShareResult(**api_response)
            else:
                log_error(logger, f"[BaiduPan]创建分享链接[{fs_id_list}]失败:[{api_response}]")
        else:
            log_error(logger, f"[BaiduPan]创建分享链接[{fs_id_list}]失败:[{response.status_code}]{response.text}")
    except Exception as e:
        log_error(logger, f"[BaiduPan]创建分享链接[{fs_id_list}]失败", e)


def verify_share_pwd(app_id: str, access_token: str, short_url: str, pwd: str) -> VerifySharePwdResult:
    """
    分享提取码验证: 本接口用于校验分享链接提取码的正确性。
    :param app_id: 	应用ID
    :param access_token: Access Token
    :param short_url: 分享短链
    :param pwd: 分享密码，长度4位，数字+小写字母组成
    :return: VerifySharePwdResult
    """
    params = {
        'product': 'netdisk',
        'appid': app_id,
        'access_token': access_token,
        'short_url': short_url
    }
    form_data = {
        'pwd': pwd,
    }
    headers = {
        'Host': 'pan.baidu.com'
    }
    try:
        post_url = 'https://pan.baidu.com/apaas/1.0/share/verify?' + http_params_tools.url_encode_params(params)
        response = requests.post(post_url, data=form_data, headers=headers)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            api_response = response.json()
            if api_response['errno'] == 0:
                return VerifySharePwdResult(**api_response)
            else:
                log_error(logger, f"[BaiduPan]验证分享提取码[{short_url}]-[{pwd}]失败:[{api_response}]")
        else:
            log_error(logger,
                      f"[BaiduPan]验证分享提取码[{short_url}]-[{pwd}]失败:[{response.status_code}]{response.text}")
    except Exception as e:
        log_error(logger, f"[BaiduPan]验证分享提取码[{short_url}]-[{pwd}]失败", e)


def query_share_info(app_id: str, access_token: str, short_url: str, s_pwd: str) -> QueryShareInfoResult:
    """
    查询分享详情: 本接口用于查询指定分享链接的链接属性信息，如创建时间、有效期等信息。
    :param app_id: 应用ID
    :param access_token: Access Token
    :param short_url: 分享短链
    :param s_pwd: 加密的提取码
    :return: QueryShareInfoResult
    """
    params = {
        'product': 'netdisk',
        'appid': app_id,
        'access_token': access_token,
        'short_url': short_url
    }
    form_data = {
        'spwd': s_pwd,
    }
    headers = {
        'Host': 'pan.baidu.com'
    }
    try:
        post_url = 'https://pan.baidu.com/apaas/1.0/share/info?' + http_params_tools.url_encode_params(params)
        response = requests.post(post_url, data=form_data, headers=headers)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            api_response = response.json()
            if api_response['errno'] == 0:
                return QueryShareInfoResult(**api_response)
            else:
                log_error(logger, f"[BaiduPan]查询分享详情[{short_url}]-[{s_pwd}]失败:[{api_response}]")
        else:
            log_error(logger,
                      f"[BaiduPan]查询分享详情[{short_url}]-[{s_pwd}]失败:[{response.status_code}]{response.text}")
    except Exception as e:
        log_error(logger, f"[BaiduPan]查询分享详情[{short_url}]-[{s_pwd}]失败", e)


def query_share_data_list(app_id: str, access_token: str, short_url: str, s_pwd: str,
                          dir_path: str = None, page_num: int = 1, page_size: int = 100) -> QueryShareDataListResult:
    """
    查询分享文件信息: 本接口用于获取分享链接内对应的文件信息，包括分享链接的创建用户、创建时间、分享的文件列表和目录结构、分享文件的大小、名称、类型、缩略图、文件ID。
    :param app_id: 应用ID
    :param access_token: Access Token
    :param short_url: 分享短链
    :param s_pwd: 加密的提取码
    :param dir_path: 分享层级目录, 空表示获取外链第一层级文件列表
    :param page_num: 分页号（当dir非空时必传；dir 非根目录时分页参数才有效）
    :param page_size: 每页大小，最大 100（当dir非空时必传）
    :return: QueryShareDataListResult
    """
    params = {
        'product': 'netdisk',
        'appid': app_id,
        'access_token': access_token,
        'short_url': short_url
    }
    form_data = {
        'spwd': s_pwd,
    }
    if dir_path:
        form_data['dir'] = dir_path
        form_data['page'] = page_num,
        form_data['page_size'] = page_size
    headers = {
        'Host': 'pan.baidu.com'
    }
    try:
        post_url = 'https://pan.baidu.com/apaas/1.0/share/info?' + http_params_tools.url_encode_params(params)
        response = requests.post(post_url, data=form_data, headers=headers)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            api_response = response.json()
            if api_response['errno'] == 0:
                return QueryShareDataListResult(**api_response)
            else:
                log_error(logger, f"[BaiduPan]获取分享链接内对应的文件信息[{short_url}]-[{s_pwd}]失败:[{api_response}]")
        else:
            log_error(logger,
                      f"[BaiduPan]获取分享链接内对应的文件信息[{short_url}]-[{s_pwd}]失败:[{response.status_code}]{response.text}")
    except Exception as e:
        log_error(logger, f"[BaiduPan]获取分享链接内对应的文件信息[{short_url}]-[{s_pwd}]失败", e)


def transfer_share(app_id: str, access_token: str, short_url: str, fs_id_list: list[str], to_pan_path: str, s_pwd: str,
                   async_value: int = 2, on_dup: str = 'newcopy') -> TransferShareResult:
    """
    分享文件转存: 本接口用于将分享链接中的内容转存到当前授权用户指定网盘目录下。
    :param app_id: 应用ID
    :param access_token: Access Token
    :param short_url: 分享短链
    :param fs_id_list: 转存文件ID，注意参数为json序列化后的字符串数组，fsid需要带单引号
    :param to_pan_path: 保存路径
    :param s_pwd: 	加密的提取码
    :param async_value: 是否异步，建议全部走异步：2
    :param on_dup: 文件冲突行为，fail-失败，newcopy-复制
    :return: TransferShareResult
    """
    params = {
        'product': 'netdisk',
        'appid': app_id,
        'access_token': access_token,
        'short_url': short_url
    }
    form_data = {
        'spwd': s_pwd,
        'fsid_list': json.dumps(fs_id_list),
        'to_path': to_pan_path,
        'async': async_value,
        'ondup': on_dup
    }
    headers = {
        'Host': 'pan.baidu.com'
    }
    try:
        post_url = 'https://pan.baidu.com/apaas/1.0/share/transfer?' + http_params_tools.url_encode_params(params)
        response = requests.post(post_url, data=form_data, headers=headers)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            api_response = response.json()
            if api_response['errno'] == 0:
                return TransferShareResult(**api_response)
            else:
                log_error(logger, f"[BaiduPan]查询分享详情[{short_url}]-[{s_pwd}]失败:[{api_response}]")
        else:
            log_error(logger,
                      f"[BaiduPan]查询分享详情[{short_url}]-[{s_pwd}]失败:[{response.status_code}]{response.text}")
    except Exception as e:
        log_error(logger, f"[BaiduPan]查询分享详情[{short_url}]-[{s_pwd}]失败", e)


def transfer_share_task_query(app_id: str, access_token: str, task_id:int) -> TransferShareTaskQueryResult:
    """
    转存任务查询: 本接口用于查询转存任务结果
    :param app_id: 	应用ID
    :param access_token: Access Token
    :param task_id: 转存接口返回的task_id
    :return: TransferShareTaskQueryResult
    """
    pass
