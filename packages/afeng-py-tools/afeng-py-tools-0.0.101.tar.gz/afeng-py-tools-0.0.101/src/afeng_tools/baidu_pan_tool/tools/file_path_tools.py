"""
百度网盘文件路径工具
"""
from typing import List

import requests

import openapi_client
from openapi_client.api.fileinfo_api import FileinfoApi
from openapi_client.api.multimediafile_api import MultimediafileApi
from afeng_tools.baidu_pan_tool.core.baidu_pan_decorator_tools import auto_fileinfo_api, auto_media_file_api
from afeng_tools.baidu_pan_tool.core.baidu_pan_models import FileInfo, DocFileInfo, ImageInfo, SearchFileInfo, SearchResultInfo, \
    MultimediaFileInfo, VideoInfo, BtInfo, CategoryListResult, CategoryListItem
from afeng_tools.http_tool import http_params_tools
from afeng_tools.log_tool.loguru_tools import get_logger, log_error

logger = get_logger()


@auto_media_file_api
def list_all_file(access_token: str, dir_path: str, recursion: int = 0,
                  order: str = 'name', desc: int = 0, web: int = 0, only_file: bool = False,
                  api_instance: MultimediafileApi = None) -> List[FileInfo]:
    """
    递归获取文件列表: 本接口可以递归获取指定目录下的所有文件列表（包括目录）。
    :param access_token: Access Token
    :param dir_path: 目录名称绝对路径，必须/开头；
    :param recursion: 是否递归，0为否，1为是，默认为0, 当目录下存在文件夹，并想获取到文件夹下的子文件时，可以设置 recursion 参数为1, 即可获取到更深目录层级的文件。
    :param order: 排序字段
                    time(修改时间)
                    name(文件名，注意，此处排序是按字符串排序的)
                    size(大小，目录无大小)，默认为文件类型
    :param desc: 0为升序，1为降序，默认为0
    :param web: 默认为0， 为1时返回缩略图地址
    :param only_file: 是否只有文件
    :param api_instance: 自动注入MultimediafileApi
    :return: List[FileInfo]
    """
    tmp_file_list = []
    _result = list_all_by_page(access_token, dir_path=dir_path, recursion=recursion, order=order, desc=desc,
                               web=web, api_instance=api_instance)
    if _result and _result.file_list:
        tmp_file_list.extend(_result.file_list)
        while _result and (_result.errno == 0 or _result.errno is None) and _result.has_more:
            _result = list_all_by_page(access_token, dir_path=dir_path, recursion=recursion, order=order, desc=desc,
                                       start=_result.cursor, web=web, api_instance=api_instance)
            if _result and _result.file_list:
                tmp_file_list.extend(_result.file_list)
        if only_file:
            tmp_file_list = filter(lambda x: x.isdir == 0, tmp_file_list)
    return tmp_file_list


@auto_media_file_api
def list_all_by_page(access_token: str, dir_path: str, recursion: int = 0,
                     order: str = 'name', desc: int = 0, start: int = 0, limit: int = 1000,
                     web: int = 0,
                     api_instance: MultimediafileApi = None) -> MultimediaFileInfo:
    """
    获取文件列表（前1000条）: 本接口可以递归获取指定目录下的文件列表。
    :param access_token: Access Token
    :param dir_path: 目录名称绝对路径，必须/开头；
    :param recursion: 是否递归，0为否，1为是，默认为0, 当目录下存在文件夹，并想获取到文件夹下的子文件时，可以设置 recursion 参数为1, 即可获取到更深目录层级的文件。
    :param order: 排序字段
                    time(修改时间)
                    name(文件名，注意，此处排序是按字符串排序的)
                    size(大小，目录无大小)，默认为文件类型
    :param desc: 0为升序，1为降序，默认为0
    :param start: 查询起点，默认为0，当返回has_more=1时，应使用返回的cursor作为下一次查询的起点
    :param limit: 查询数目，默认为1000； 如果设置start和limit参数，则建议最大设置为1000
    :param web: 默认为0， 为1时返回缩略图地址
    :param api_instance: 自动注入MultimediafileApi
    :return: MultimediaFileInfo
    """
    try:
        api_response = api_instance.xpanfilelistall(access_token, dir_path, recursion,
                                                    order=order, desc=desc, start=start, limit=limit,
                                                    web=str(web))
        if api_response['errno'] == 0:

            multi_info = MultimediaFileInfo(
                has_more=api_response['has_more'] == 1,
                cursor=api_response['cursor']
            )
            multi_info.file_list = [FileInfo(**tmp_data) for tmp_data in api_response['list']]
            return multi_info
        elif api_response['errno'] == 42213:
            log_error(logger, f"[BaiduPan]文件或目录[{dir_path}]无权访问搜索")
        elif api_response['errno'] == 31066:
            log_error(logger, f"[BaiduPan]文件或目录[{dir_path}]不存在，无法进行搜索")
        elif api_response['errno'] == 31034:
            log_error(logger, f"[{dir_path}]命中频控,listall接口的请求频率建议不超过每分钟8-10次")
        else:
            log_error(logger, f"[BaiduPan]搜索目录[{dir_path}]下文件列表失败，api_response: {api_response}")
    except openapi_client.ApiException as e:
        log_error(logger, "[BaiduPan]Exception when calling MultimediafileApi->xpanfilelistall", e)


@auto_fileinfo_api
def list_file_by_page(access_token: str, dir_path: str = '/', order: str = 'name', desc: int = 0,
                      start: int = 0, limit: int = 1000, web: int = 0, folder: int = 0, show_empty: int = 1,
                      api_instance: FileinfoApi = None) -> list[FileInfo]:
    """
    获取文件列表（前1000条）: 本接口用于获取用户网盘中指定目录下的文件列表。返回的文件列表支持排序、分页等操作。
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
    :param api_instance: 自动注入的 FileinfoApi
    :return:
    """
    try:
        api_response = api_instance.xpanfilelist(access_token, dir=dir_path,
                                                 start=str(start), limit=limit,
                                                 order=order, desc=desc, web=str(web),
                                                 folder=str(folder), showempty=show_empty)
        if api_response['errno'] == 0:
            return [FileInfo(**tmp_data) for tmp_data in api_response['list']]
        elif api_response['errno'] == -7:
            log_error(logger, f"文件或目录[{dir_path}]无权访问，响应信息：{api_response}")
        elif api_response['errno'] == -9:
            log_error(logger, f"文件或目录[{dir_path}]不存在，响应信息：{api_response}")
        else:
            log_error(logger, f"获取目录[{dir_path}]下文件列表失败，响应信息：{api_response}")
    except openapi_client.ApiException as e:
        log_error(logger, "[BaiduPan]Exception when calling FileinfoApi->xpanfilelist", e)


@auto_fileinfo_api
def list_image(access_token: str, dir_path: str = '/',
               page_num: int = None, page_size: int = 1000,
               order: str = 'name', desc: int = 1,
               recursion: int = 0, web: int = 0,
               api_instance: FileinfoApi = None) -> List[ImageInfo]:
    """
     获取图片列表（前1000条）: 获取用户指定目录下的图片列表
     :param access_token: Access Token
     :param dir_path: 目录名称，以/开头的绝对路径, 默认为/ , 路径包含中文时需要UrlEncode编码
     :param page_num: 页码，从1开始， 如果不指定页码，则为不分页模式，返回所有的结果。如果指定page参数，则按修改时间倒序排列
     :param page_size: 一页返回的文档数， 默认值为1000，建议最大值不超过1000
     :param order:  排序字段：默认为name
                        time按修改时间排序，
                        name按文件名称排序，
                        size按文件大小排序，
     :param desc: 0为升序，1为降序，默认为1
     :param recursion:  是否需要递归，0为不需要，1为需要，默认为0, 递归是指：当目录下有文件夹，使用此参数，可以获取到文件夹下面的文档
     :param web: 为1时返回文档预览地址lodocpreview
     :param api_instance: 自动注入的 FileinfoApi
     :return: List[ImageInfo]
     """
    try:
        api_response = api_instance.xpanfileimagelist(access_token, parent_path=dir_path,
                                                      recursion=str(recursion),
                                                      page=page_num, num=page_size,
                                                      order=order, desc=desc, web=str(web))
        if api_response['errno'] == 0:
            return [ImageInfo(**tmp_data) for tmp_data in api_response['info']]
        else:
            log_error(logger, f"[BaiduPan]获取目录[{dir_path}]下图片列表失败:{api_response}")
    except openapi_client.ApiException as e:
        log_error(logger, "[BaiduPan]Exception when calling FileinfoApi->xpanfileimagelist", e)


@auto_fileinfo_api
def list_doc(access_token: str, dir_path: str = '/',
             page_num: int = None, page_size: int = 1000,
             order: str = 'name', desc: int = 1,
             recursion: int = 0, web: int = 0,
             api_instance: FileinfoApi = None) -> List[DocFileInfo]:
    """
    获取文档列表（前1000条）：获取用户指定目录下的文档列表。
    :param access_token: Access Token
    :param dir_path: 目录名称，以/开头的绝对路径, 默认为/
    :param page_num: 页码，从1开始， 如果不指定页码，则为不分页模式，返回所有的结果。如果指定page参数，则按修改时间倒序排列
    :param page_size: 一页返回的文档数， 默认值为1000，建议最大值不超过1000
    :param order:  排序字段： 默认为name
                        time按修改时间排序
                        name按文件名称排序
                        size按文件大小排序
    :param desc: 0为升序，1为降序，默认为1
    :param recursion:  是否需要递归，0为不需要，1为需要，默认为0, 递归是指：当目录下有文件夹，使用此参数，可以获取到文件夹下面的文档
    :param web: 为1时返回文档预览地址lodocpreview
    :param api_instance: 自动注入的 FileinfoApi
    :return: List[DocFileInfo]
    """
    try:
        api_response = api_instance.xpanfiledoclist(access_token, parent_path=dir_path, order=order, desc=desc,
                                                    recursion=str(recursion), page=page_num, num=page_size,
                                                    web=str(web))
        if api_response['errno'] == 0:
            return [DocFileInfo(**tmp_data) for tmp_data in api_response['info']]
        else:
            log_error(logger, f"[BaiduPan][{dir_path}]下文档列表失败: {api_response}")
    except openapi_client.ApiException as e:
        log_error(logger, "[BaiduPan]Exception when calling FileinfoApi->xpanfiledoclist", e)


def list_video(access_token: str, dir_path: str = '/',
               page_num: int = None, page_size: int = 1000,
               order: str = 'name', desc: int = 1,
               recursion: int = 0, web: int = 0) -> list[VideoInfo]:
    """
    获取视频列表: 本接口用于获取用户指定目录下的视频列表.
    :param access_token: Access Token
    :param dir_path: 目录名称，以/开头的绝对路径, 默认为/
    :param page_num: 页码，从1开始， 如果不指定页码，则为不分页模式，返回所有的结果。如果指定page参数，则按修改时间倒序排列
    :param page_size: 一页返回的文件数， 默认值为1000, 最大值建议不超过1000
    :param order: 排序字段， 默认为name
                    time按修改时间排序
                    name按文件名称排序(注意，此处排序是按字符串排序的）
                    size按文件大小排序
    :param desc: 0为升序，1为降序，默认为1
    :param recursion: 是否需要递归，0为不需要，1为需要，默认为0
                        递归是指：当目录下有文件夹，使用此参数，可以获取到文件夹下面的视频
    :param web: 为1时返回视频预览缩略图
    :return: list[VideoInfo]
    """
    params = {
        'method': 'videolist',
        'access_token': access_token,
        'parent_path': http_params_tools.url_encode(dir_path),
        'page': page_num,
        'num': page_size,
        'order': order,
        'desc': desc,
        'recursion': recursion,
        'web': web
    }
    headers = {
        'User-Agent': 'pan.baidu.com'
    }
    try:
        response = requests.get('http://pan.baidu.com/rest/2.0/xpan/file', params=params, headers=headers)
        response.encoding = 'utf8'
        api_response = response.json()
        if api_response['errno'] == 0:
            return [VideoInfo(**tmp_data) for tmp_data in api_response['info']]
        else:
            log_error(logger, f"[BaiduPan][{dir_path}]下视频列表失败: {api_response}")
    except openapi_client.ApiException as e:
        log_error(logger, "[BaiduPan]Exception when calling FileinfoApi->xpanfilevideolist", e)


def list_bt(access_token: str, dir_path: str = '/',
            page_num: int = None, page_size: int = 1000,
            order: str = 'name', desc: int = 1,
            recursion: int = 0) -> list[BtInfo]:
    """
    获取bt列表: 本接口用于获取用户指定路径下的bt文件列表。
    :param access_token: Access Token
    :param dir_path: 目录名称，以/开头的绝对路径, 默认为/
    :param page_num: 页码，从1开始， 如果不指定页码，则为不分页模式，返回所有的结果。如果指定page参数，则按修改时间倒序排列
    :param page_size: 一页返回的文件数， 默认值为1000, 最大值建议不超过1000
    :param order: 排序字段， 默认为name
                    time按修改时间排序
                    name按文件名称排序(注意，此处排序是按字符串排序的）
                    size按文件大小排序
    :param desc: 0为升序，1为降序，默认为1
    :param recursion: 是否需要递归，0为不需要，1为需要，默认为0
                        递归是指：当目录下有文件夹，使用此参数，可以获取到文件夹下面的bt文件
    :return: list[BtInfo]
    """
    params = {
        'method': 'btlist',
        'access_token': access_token,
        'parent_path': http_params_tools.url_encode(dir_path),
        'page': page_num,
        'num': page_size,
        'order': order,
        'desc': desc,
        'recursion': recursion,
    }
    headers = {
        'User-Agent': 'pan.baidu.com',
        'Cookie': 'PANWEB=1; BAIDUID=AC26BE01592777C2F2253ECBC0E5780B:FG=1'
    }
    try:
        response = requests.get('http://pan.baidu.com/rest/2.0/xpan/file', params=params, headers=headers)
        response.encoding = 'utf8'
        api_response = response.json()
        if api_response['errno'] == 0:
            return [BtInfo(**tmp_data) for tmp_data in api_response['info']]
        else:
            log_error(logger, f"[BaiduPan][{dir_path}]下bt列表失败: {api_response}")
    except openapi_client.ApiException as e:
        log_error(logger, "[BaiduPan]Exception when calling FileinfoApi->xpanfilebtlist", e)


@auto_fileinfo_api
def search(access_token: str, key_word: str, dir_path: str = '/', category: int = None,
           page_num: str = None, page_size: int = 500,
           recursion: str = '0', web: str = '0', device_id: str = None,
           api_instance: FileinfoApi = None) -> SearchResultInfo:
    """
    搜索文件: 本接口用于获取用户指定目录下，包含指定关键字的文件列表。
    :param access_token: Access T
    :param key_word: 搜索关键字，最大30字符（UTF8格式）
    :param dir_path: 搜索目录，默认根目录
    :param category: 文件类型，1 视频、2 音频、3 图片、4 文档、5 应用、6 其他、7 种子
    :param page_num: 页数，从1开始，缺省则返回所有条目
    :param page_size: 默认为500，不能修改
    :param recursion: 是否递归，带这个参数就会递归，否则不递归
    :param web: 是否展示缩略图信息，带这个参数会返回缩略图信息，否则不展示缩略图信息
    :param device_id: 设备ID，设备注册接口下发，硬件设备必传
    :param api_instance: 自动注入的 FileinfoApi
    :return: SearchResultInfo
    """
    try:
        api_response = api_instance.xpanfilesearch(access_token, key=key_word, dir=dir_path, category=category,
                                                   num=page_num, page=page_size,
                                                   recursion=recursion, web=web,
                                                   device_id=device_id)
        if api_response['errno'] == 0:
            result = SearchResultInfo(has_more=api_response['has_more'] == 1,
                                      content_list=api_response['contentlist'])
            result.file_list = [SearchFileInfo(**tmp_data) for tmp_data in api_response['list']]
            return result
        elif api_response['errno'] == -7:
            log_error(logger, f"[BaiduPan]目录[{dir_path}]无权访问搜索")
        elif api_response['errno'] == -9:
            log_error(logger, f"[BaiduPan]目录[{dir_path}]不存在，无法进行搜索")
        else:
            log_error(logger, f"[BaiduPan]搜索目录[{dir_path}]下文件[{key_word}]失败: {api_response}")
    except openapi_client.ApiException as e:
        log_error(logger, "[BaiduPan]Exception when calling FileinfoApi->xpanfilesearch", e)


def list_category_file(access_token: str, category: int, dir_path: str = '/',
                       show_dir: int = 0, recursion: int = 0, ext: str = None,
                       start: int = 0, limit: int = 1000,
                       order: str = 'name', desc: int = 1, device_id: str = None) -> CategoryListResult:
    """
    获取分类文件列表: 本接口用于获取用户目录下指定类型的文件列表。
    :param access_token: Access Token
    :param category: 文件类型，1 视频、2 音频、3 图片、4 文档、5 应用、6 其他、7 种子, 多个category使用英文逗号分隔，示例：3,4
    :param dir_path: 目录名称，以/开头的绝对路径, 默认为/
    :param show_dir: 是否展示文件夹，0:否(默认) 1:是
    :param recursion: 是否需要递归，0为不需要，1为需要，默认为0 （注意recursion=1时不支持show_dir=1）
    :param ext: 需要的文件格式，多个格式以英文逗号分隔，示例: txt,epub，默认为category下所有格式
    :param start: 查询起点，默认为0
    :param limit: 查询数目，最大1000，默认1000
    :param order: 排序字段， 默认为name
                    time按修改时间排序
                    name按文件名称排序(注意，此处排序是按字符串排序的）
                    size按文件大小排序
    :param desc: 0为升序，1为降序，默认为1
    :param device_id: 设备ID，硬件设备必传
    :return: CategoryListResult
    """
    params = {
        'method': 'categorylist',
        'access_token': access_token,
        'category': category,
        'show_dir': show_dir,
        'parent_path': http_params_tools.url_encode(dir_path),
        'recursion': recursion,
        'ext': ext,
        'start': start,
        'limit': limit,
        'order': order,
        'desc': desc,
        'device_id': device_id
    }
    headers = {
        'User-Agent': 'pan.baidu.com'
    }
    try:
        response = requests.get('http://pan.baidu.com/rest/2.0/xpan/multimedia', params=params, headers=headers)
        response.encoding = 'utf8'
        api_response = response.json()
        if api_response['errno'] == 0:
            result = CategoryListResult(has_more=api_response['has_more'] == 1,
                                        cursor=api_response['cursor'])
            result.file_list = [CategoryListItem(**tmp_data) for tmp_data in api_response['list']]
            return result
        else:
            log_error(logger, f"[BaiduPan]获取[{dir_path}]下分类[{category}]文件列表失败: {api_response}")
    except openapi_client.ApiException as e:
        log_error(logger, "[BaiduPan]Exception when calling multimedia->categorylist", e)
