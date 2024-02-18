"""
百度网盘音频文件工具
"""
import requests

from afeng_tools.baidu_pan_tool.core.baidu_pan_models import ListAudioCategoryResult, AudioCategoryInfo, ListAudioResult, AudioInfo
from afeng_tools.http_tool import http_params_tools
from afeng_tools.log_tool.loguru_tools import get_logger, log_error

logger = get_logger()


def list_audio_category(access_token: str, page_num: int = 1, page_size: int = 20) -> ListAudioCategoryResult:
    """
    获取播单列表: 本接口用于查询用户下的所有播单。
    :param access_token: Access Token
    :param page_num: 当前页数 ，默认1
    :param page_size: 每页返回的播单数目，默认20
    :return: ListAudioCategoryResult
    """
    params = {
        'method': 'list',
        'access_token': access_token,
        'page': page_num,
        'psize': page_size
    }
    headers = {
        'Host': 'pan.baidu.com'
    }
    try:
        response = requests.get('http://pan.baidu.com/rest/2.0/xpan/broadcast/list', params=params, headers=headers)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            api_response = response.json()
            if api_response['errno'] == 0:
                result = ListAudioCategoryResult(errno=api_response.get('errno'),
                                                 request_id=api_response.get('request_id'),
                                                 show_msg=api_response.get('show_msg'),
                                                 newno=api_response.get('newno'),
                                                 has_more=api_response.get('has_more'))
                if api_response.get('list'):
                    result.data_list = [AudioCategoryInfo(**tmp) for tmp in api_response.get('list')]
                return result
            else:
                log_error(logger, f"[BaiduPan]获取播单列表失败:[{api_response}]")
        else:
            log_error(logger, f"[BaiduPan]获取播单列表失败:[{response.status_code}]{response.text}")
    except Exception as e:
        log_error(logger, f"[BaiduPan]获取播单列表失败", e)


def list_audio(access_token: str, mb_id: int, show_meta: int = 0,
               page_num: int = 1, page_size: int = 20) -> ListAudioResult:
    """
    获取播单下文件列表
    :param access_token: 本接口用于根据播单id获取播单内文件列表。
    :param mb_id: 播单id, 该值通过list_audio_category()获取播单列表获取
    :param show_meta: showmeta=1，可展示文件详细信
    :param page_num: 当前页数，默认1
    :param page_size: 每页返回的播单数目，默认20
    :return:
    """
    params = {
        'access_token': access_token,
        'mb_id': mb_id,
        'showmeta': show_meta,
        'page': page_num,
        'psize': page_size
    }
    headers = {
        'Host': 'pan.baidu.com'
    }
    try:
        response = requests.get('http://pan.baidu.com/rest/2.0/xpan/broadcast/filelist', params=params, headers=headers)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            api_response = response.json()
            if api_response['errno'] == 0:
                result = ListAudioResult(errno=api_response.get('errno'),
                                         request_id=api_response.get('request_id'),
                                         show_msg=api_response.get('show_msg'),
                                         newno=api_response.get('newno'),
                                         has_more=api_response.get('has_more'))
                if api_response.get('list'):
                    result.data_list = [AudioInfo(**tmp) for tmp in api_response.get('list')]
                return result
            else:
                log_error(logger, f"[BaiduPan]获取播单[{mb_id}]列表失败:[{api_response}]")
        else:
            log_error(logger, f"[BaiduPan]获取播单[{mb_id}]列表失败:[{response.status_code}]{response.text}")
    except Exception as e:
        log_error(logger, f"[BaiduPan]获取播单[{mb_id}]列表失败", e)


def _get_audio_type(pan_path: str):
    """获取音频分片格式"""
    if pan_path.endswith('.mp3'):
        return 'M3U8_MP3_128'
    else:
        return 'M3U8_HLS_MP3_128'


def get_audio_m3u8_url(access_token: str, pan_path: str) -> tuple[str, dict[str, str]]:
    """
    获取音频播放的m3u8地址(可以使用百度web播放器播放：https://cloud.baidu.com/doc/MCT/s/zjwvz4w4z)
    :param access_token:
    :param pan_path:
    :return: (m3u8_url,headers)
    """
    params = {
        'method': 'streaming',
        'access_token': access_token,
        'path': pan_path,
        'type': _get_audio_type(pan_path)
    }
    headers = {
        'User-Agent': 'xpanvideo;netdisk;iPhone13;ios-iphone;15.1;ts',
        'Host': 'pan.baidu.com'
    }
    m3u8_url = 'http://pan.baidu.com/rest/2.0/xpan/file?' + http_params_tools.url_encode_params(params)
    return m3u8_url, headers
