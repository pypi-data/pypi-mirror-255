"""
获取文件元信息工具
"""
import requests

import openapi_client
from openapi_client.api.multimediafile_api import MultimediafileApi
from afeng_tools.baidu_pan_tool.core.baidu_pan_decorator_tools import auto_media_file_api
from afeng_tools.baidu_pan_tool.core.baidu_pan_models import FileMetaInfo, CategoryCountInfo
from afeng_tools.http_tool import http_params_tools
from afeng_tools.log_tool.loguru_tools import get_logger, log_error

logger = get_logger()


@auto_media_file_api
def get_file_metas(access_token: str, fs_id_list: list[int], d_link: int = 0,
                   thumb: int = 0, extra: int = 0, need_media: int = 0,
                   api_instance: MultimediafileApi = None) -> list[FileMetaInfo]:
    """
    查询文件信息: 本接口可用于获取用户指定文件的meta信息。支持查询多个或一个文件的meta信息，meta信息包括文件名字、文件创建时间、文件的下载地址等。
    :param access_token: Access Token
    :param fs_id_list: 文件id数组，数组中元素是uint64类型，数组大小上限是：100
    :param d_link: 是否需要下载地址，0为否，1为是，默认为0。
    :param thumb: 是否需要缩略图地址，0为否，1为是，默认为0
    :param extra: 图片是否需要拍摄时间、原图分辨率等其他信息，0 否、1 是，默认0
    :param need_media: 视频是否需要展示时长信息，needmedia=1时，返回 duration 信息时间单位为秒 （s），转换为向上取整。 0 否、1 是，默认0

    :param api_instance:
    :return:
    """
    try:
        api_response = api_instance.xpanmultimediafilemetas(access_token,
                                                            fsids=f"[{','.join([str(tmp) for tmp in fs_id_list])}]",
                                                            thumb=str(thumb), extra=str(extra), dlink=str(d_link),
                                                            needmedia=need_media)
        print(api_response)
        if api_response['errno'] == 0:
            return [FileMetaInfo(**tm_data) for tm_data in api_response['list']]
        else:
            log_error(logger, f"[BaiduPan]查询文件{fs_id_list}元信息失败，api_response: {api_response}")
    except openapi_client.ApiException as e:
        log_error(logger, "[BaiduPan]Exception when calling MultimediafileApi->xpanmultimediafilemetas", e)


def list_category_info(access_token: str, dir_path: str = '/',
                       category: int = None, recursion: int = 0) -> dict[int, CategoryCountInfo]:
    """
    获取分类文件总个数: 本接口用于获取用户指定目录下指定类型的文件数量。
    :param access_token: Access Token
    :param dir_path: 目录名称，以/开头的绝对路径, 默认为/
    :param category: 文件类型，1 视频、2 音频、3 图片、4 文档、5 应用、6 其他、7 种子
    :param recursion: 是否需要递归，0为不需要，1为需要，默认为0
                        递归是指：当目录下有文件夹，使用此参数，可以获取到文件夹下面的bt文件
    :return: {category:CategoryCountInfo}
    """
    params = {
        'method': 'btlist',
        'access_token': access_token,
        'parent_path': http_params_tools.url_encode(dir_path),
        'category': category,
        'recursion': recursion,
    }
    headers = {
        'User-Agent': 'pan.baidu.com'
    }
    try:
        response = requests.get('http://pan.baidu.com/rest/2.0/xpan/file', params=params, headers=headers)
        response.encoding = 'utf8'
        api_response = response.json()
        if api_response['errno'] == 0:
            return {int(tmp_key): CategoryCountInfo(**api_response['info'].get(tmp_key)) for tmp_key in
                    api_response['info'].keys()}
        else:
            log_error(logger, f"[BaiduPan][{dir_path}]下获取分类文件总个数: {api_response}")
    except openapi_client.ApiException as e:
        log_error(logger, "[BaiduPan]Exception when calling MultimediafileApi->xpanlistcategory", e)
