"""
百度网盘视频文件工具
"""
from typing import Literal

import requests

from afeng_tools.baidu_pan_tool.core.baidu_pan_models import AdTokenResult
from afeng_tools.baidu_pan_tool.tools.user_tools import get_user_info
from afeng_tools.http_tool import http_params_tools
from afeng_tools.log_tool.loguru_tools import log_error, get_logger

logger = get_logger()


def _get_video_type(pan_path: str, video_resolution: Literal[480, 720, 1080] | int = 480):
    """
    获取视频分片格式
    :param pan_path: 视频的网盘路径
    :param video_resolution: 视频分辨率
    :return:视频分片格式
    """
    if pan_path.endswith('.flv'):
        return 'M3U8_FLV_264_480'
    else:
        return f'M3U8_AUTO_{video_resolution}'


def _get_ad_token(access_token: str, pan_path: str) -> AdTokenResult:
    """
    获取音频播放的m3u8地址(可以使用百度web播放器播放：https://cloud.baidu.com/doc/MCT/s/zjwvz4w4z)
    :param access_token: Access Token
    :param pan_path: 视频的网盘路径
    :return: AdTokenResult
    """
    params = {
        'method': 'streaming',
        'access_token': access_token,
        'path': pan_path,
        'type': _get_video_type(pan_path),
    }
    headers = {
        'User-Agent': 'xpanvideo;netdisk;iPhone13;ios-iphone;15.1;ts',
        'Host': 'pan.baidu.com'
    }
    try:
        response = requests.get('https://pan.baidu.com/rest/2.0/xpan/file', params=params, headers=headers)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            api_response = response.json()
            if api_response['errno'] == 0:
                return AdTokenResult(**api_response)
            else:
                log_error(logger, f"[BaiduPan]第一次请求获取视频流[{pan_path}]失败:[{api_response}]")
        else:
            log_error(logger, f"[BaiduPan]第一次请求获取视频流[{pan_path}]失败:[{response.status_code}]{response.text}")
    except Exception as e:
        log_error(logger, f"[BaiduPan]第一次请求获取视频流[{pan_path}]失败", e)


def get_video_m3u8_url(access_token: str, pan_path: str) -> tuple[str, dict[str, str]]:
    """
    获取视频播放的m3u8地址
    :param access_token: Access Token
    :param pan_path: 视频的网盘路径
    :return: (m3u8_url,headers)
    """
    user_info = get_user_info(access_token)
    ad_token = ''
    # 会员类型，0普通用户、1普通会员、2超级会员
    if user_info.vip_type < 2:
        ad_token = _get_ad_token(access_token, pan_path=pan_path).adToken
    params = {
        'method': 'streaming',
        'access_token': access_token,
        'path': pan_path,
        'type': _get_video_type(pan_path),
    }
    if ad_token:
        params['adToken'] = ad_token
    headers = {
        'User-Agent': 'xpanvideo;netdisk;iPhone13;ios-iphone;15.1;ts',
        'Host': 'pan.baidu.com'
    }
    m3u8_url = 'http://pan.baidu.com//rest/2.0/xpan/file?' + http_params_tools.url_encode_params(params)
    return m3u8_url, headers


def get_video_m3u8_subtitle_url(access_token: str, pan_path: str) -> tuple[str, dict[str, str]]:
    """
    获取视频字幕URL：本接口用于获取网盘视频文件字幕。
    :param access_token: Access Token
    :param pan_path: 视频的网盘路径
    :return: (m3u8_url,headers)
    """
    params = {
        'method': 'streaming',
        'access_token': access_token,
        'path': pan_path,
        'type': 'M3U8_SUBTITLE_SRT',
    }
    headers = {
        'User-Agent': 'xpanvideo;netdisk;iPhone13;ios-iphone;15.1;ts',
        'Host': 'pan.baidu.com'
    }
    m3u8_url = 'https://pan.baidu.com/rest/2.0/xpan/file?' + http_params_tools.url_encode_params(params)
    return m3u8_url, headers
