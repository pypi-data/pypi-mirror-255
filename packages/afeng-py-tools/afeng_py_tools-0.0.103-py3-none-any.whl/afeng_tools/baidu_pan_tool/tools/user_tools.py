"""
百度网盘用户工具
"""
import openapi_client
from openapi_client.api.userinfo_api import UserinfoApi
from afeng_tools.baidu_pan_tool.core.baidu_pan_decorator_tools import auto_userinfo_api
from afeng_tools.baidu_pan_tool.core.baidu_pan_models import UserInfo, PanVolumeInfo
from afeng_tools.log_tool.loguru_tools import log_error, get_logger

logger = get_logger()


@auto_userinfo_api
def get_user_info(access_token: str, api_instance: UserinfoApi = None) -> UserInfo:
    """
    获取用户信息：本接口用于获取用户的基本信息，包括账号、头像地址、会员类型等。
    :return:
    """
    try:
        api_response = api_instance.xpannasuinfo(access_token)
        if api_response['errno'] == 0:
            return UserInfo(
                baidu_name=api_response['baidu_name'],
                net_disk_name=api_response['netdisk_name'],
                avatar_url=api_response['avatar_url'],
                vip_type=api_response['vip_type'],
                uk=api_response['uk']
            )
        else:
            log_error(logger, '[BaiduPan]获取用户信息失败，api_response：' + api_response)
    except openapi_client.ApiException as e:
        log_error(logger, "[BaiduPan]Exception when calling UserinfoApi->xpannasuinfo", e)


@auto_userinfo_api
def get_pan_info(access_token: str, check_free: int = 0, check_expire: int = 0,
                 api_instance: UserinfoApi = None) -> PanVolumeInfo:
    """
    获取网盘容量信息：本接口用于获取用户的网盘空间的使用情况，包括总空间大小，已用空间和剩余可用空间情况。
    :param access_token: Access Token
    :param check_free: 默认为0, 是否检查免费信息，0为不查，1为查
    :param check_expire: 是否检查过期信息，0为不查，1为查，默认为0
    :param api_instance: 自动注入的 UserinfoApi
    :return:
    """
    try:
        api_response = api_instance.apiquota(access_token, checkexpire=check_expire, checkfree=check_free)
        if api_response['errno'] == 0:
            return PanVolumeInfo(
                total=api_response['total'],
                expire=api_response['expire'],
                used=api_response['used'],
                free=api_response['free']
            )
        else:
            log_error(logger, '[BaiduPan]获取网盘空间失败，api_response：' + api_response)
    except openapi_client.ApiException as e:
        log_error(logger, "[BaiduPan]Exception when calling UserinfoApi->apiquota", e)
