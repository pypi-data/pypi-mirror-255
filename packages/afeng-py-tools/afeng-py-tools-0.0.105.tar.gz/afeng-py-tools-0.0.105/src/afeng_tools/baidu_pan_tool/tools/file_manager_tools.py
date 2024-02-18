"""
百度网盘文件管理工具
"""
import json
from typing import List, Literal

import requests

import openapi_client
from openapi_client.api.filemanager_api import FilemanagerApi
from afeng_tools.baidu_pan_tool.core.baidu_pan_decorator_tools import auto_file_manager_api
from afeng_tools.baidu_pan_tool.core.baidu_pan_models import CreatePathResult, CopyFileInfo, FileAsyncManageResult, \
    FileSyncManageResultItem, MoveFileInfo, RenameFileInfo
from afeng_tools.http_tool import http_params_tools
from afeng_tools.log_tool.loguru_tools import get_logger, log_error

logger = get_logger()


@auto_file_manager_api
def copy_file(access_token: str, copy_file_list: List[CopyFileInfo],
              async_flag: Literal[0, 1, 2] | int = 1,
              on_dup: Literal['fail', 'newcopy', 'overwrite', 'skip'] | str = 'newcopy',
              api_instance: FilemanagerApi = None) -> FileAsyncManageResult | List[FileSyncManageResultItem]:
    """
    复制文件
    :param access_token: Access Token
    :param copy_file_list: 待 Copy文件集合
    :param async_flag: 0 同步，1 自适应，2 异步; 设置async参数为0或2时，则服务端一定会按照同步或异步方式处理，async参数为1时，则服务端按照文件数目自适应选择同步或异步方式，以返回的taskid为准。
    :param on_dup: 全局ondup,遇到重复文件的处理策略, fail(默认，直接返回失败)、newcopy(重命名文件)、overwrite、skip
    :param api_instance: 自动注入 FilemanagerApi
    :return: FileAsyncManageResult|List[FileSyncManageResultItem]
    """
    file_list = [{'path': tmp.source_file,
                  'dest': tmp.dest_path,
                  'newname': tmp.new_filename,
                  'ondup': tmp.ondup if tmp.ondup else on_dup
                  } for tmp in copy_file_list]
    # '[{"path":"/test/123456.docx","dest":"/test/abc","newname":"123.docx","ondup":"overwrite"}]'
    file_list_str = json.dumps(file_list)
    try:
        api_response = api_instance.filemanagercopy(access_token, _async=async_flag, filelist=file_list_str)
        if api_response['errno'] == 0:
            if api_response.get('taskid'):
                return FileAsyncManageResult(taskid=api_response['taskid'])
            return [
                FileSyncManageResultItem(path=http_params_tools.url_decode(tmp_data['path']), errno=tmp_data['errno'])
                for tmp_data in api_response['info']]
        elif api_response['errno'] == -9:
            log_error(logger, f"[BaiduPan]copy[{file_list_str}]文件不存在: {api_response}")
        elif api_response['errno'] == 111:
            log_error(logger, f"[BaiduPan]copy[{file_list_str}]文件时，有其他异步任务正在执行: {api_response}")
        elif api_response['errno'] == -7:
            log_error(logger, f"[BaiduPan]copy[{file_list_str}]文件时，文件名非法: {api_response}")
        else:
            log_error(logger, f"[BaiduPan]copy[{file_list_str}]文件失败:{api_response}")
    except openapi_client.ApiException as e:
        log_error(logger, f"[BaiduPan]{file_list_str}Exception when calling FilemanagerApi->filemanagercopy", e)


@auto_file_manager_api
def rename_file(access_token: str, rename_file_list: List[RenameFileInfo],
                async_flag: Literal[0, 1, 2] | int = 1,
                on_dup: Literal['fail', 'newcopy', 'overwrite', 'skip'] | str = 'newcopy',
                api_instance: FilemanagerApi = None) -> FileAsyncManageResult | List[FileSyncManageResultItem]:
    """
    重命名文件
    :param access_token: Access Token
    :param rename_file_list: 待rename文件集合
    :param async_flag: 0 同步，1 自适应，2 异步; 设置async参数为0或2时，则服务端一定会按照同步或异步方式处理，async参数为1时，则服务端按照文件数目自适应选择同步或异步方式，以返回的taskid为准。
    :param on_dup: 全局ondup,遇到重复文件的处理策略, fail(默认，直接返回失败)、newcopy(重命名文件)、overwrite、skip
    :param api_instance: 自动注入 FilemanagerApi
    :return: FileAsyncManageResult|List[FileSyncManageResultItem]:
    """
    file_list = [{'path': tmp.source_file,
                  'newname': tmp.new_filename,
                  } for tmp in rename_file_list]
    # '[{"path":"/test/123456.docx","newname":"123.docx"}]'
    rename_list_str = json.dumps(file_list)
    try:
        api_response = api_instance.filemanagerrename(access_token, _async=async_flag,
                                                      filelist=rename_list_str, ondup=on_dup)
        if api_response['errno'] == 0:
            if api_response.get('taskid'):
                return FileAsyncManageResult(taskid=api_response['taskid'])
            return [
                FileSyncManageResultItem(path=http_params_tools.url_decode(tmp_data['path']), errno=tmp_data['errno'])
                for tmp_data in api_response['info']]
        elif api_response['errno'] == -9:
            log_error(logger, f"[BaiduPan]rename文件{rename_list_str}不存在:{api_response}")
        elif api_response['errno'] == 111:
            log_error(logger, f"[BaiduPan]rename文件{rename_list_str}时，有其他异步任务正在执行: {api_response}")
        elif api_response['errno'] == -7:
            log_error(logger, f"[BaiduPan]rename文件{rename_list_str}时，文件名非法: {api_response}")
        else:
            log_error(logger, f"[BaiduPan]rename文件{rename_list_str}失败: {api_response}")
    except openapi_client.ApiException as e:
        log_error(logger, f"[BaiduPan]{rename_list_str}Exception when calling FilemanagerApi->filemanagerrename", e)


@auto_file_manager_api
def move_file(access_token: str, move_file_list: List[MoveFileInfo],
              async_flag: Literal[0, 1, 2] | int = 1,
              on_dup: Literal['fail', 'newcopy', 'overwrite', 'skip'] | str = 'newcopy',
              api_instance: FilemanagerApi = None) -> FileAsyncManageResult | List[FileSyncManageResultItem]:
    """
    移动文件
    :param access_token: Access Token
    :param move_file_list: 待move文件集合
    :param async_flag: 0 同步，1 自适应，2 异步; 设置async参数为0或2时，则服务端一定会按照同步或异步方式处理，async参数为1时，则服务端按照文件数目自适应选择同步或异步方式，以返回的taskid为准。
    :param on_dup: 全局ondup,遇到重复文件的处理策略, fail(默认，直接返回失败)、newcopy(重命名文件)、overwrite、skip
    :param api_instance: 自动注入 FilemanagerApi
    :return: FileAsyncManageResult|List[FileSyncManageResultItem]
    """
    file_list = [{'path': tmp.source_file,
                  'dest': tmp.dest_path,
                  'newname': tmp.new_filename,
                  'ondup': tmp.ondup if tmp.ondup else on_dup
                  } for tmp in move_file_list]
    # '[{"path":"/test/123456.docx","dest":"/test/abc","newname":"123456.docx","ondup":"overwrite"}]'
    move_list_str = json.dumps(file_list)
    try:
        api_response = api_instance.filemanagermove(access_token, _async=async_flag, filelist=move_list_str)
        if api_response['errno'] == 0:
            if api_response.get('taskid'):
                return FileAsyncManageResult(taskid=api_response['taskid'])
            return [
                FileSyncManageResultItem(path=http_params_tools.url_decode(tmp_data['path']), errno=tmp_data['errno'])
                for tmp_data in api_response['info']]
        elif api_response['errno'] == -9:
            log_error(logger, f"[BaiduPan]move{move_list_str}文件不存在: {api_response}")
        elif api_response['errno'] == 111:
            log_error(logger, f"[BaiduPan]move{move_list_str}文件时，有其他异步任务正在执行: {api_response}")
        elif api_response['errno'] == -7:
            log_error(logger, f"[BaiduPan]move{move_list_str}文件时，文件名非法: {api_response}")
        else:
            log_error(logger, f"[BaiduPan]move{move_list_str}文件失败：{api_response}")
    except openapi_client.ApiException as e:
        log_error(logger, f"[BaiduPan]{move_list_str}Exception when calling FilemanagerApi->filemanagermove", e)


@auto_file_manager_api
def delete_file(access_token: str, delete_file_list: List[str],
                async_flag: Literal[0, 1, 2] | int = 1,
                api_instance: FilemanagerApi = None) -> FileAsyncManageResult | List[FileSyncManageResultItem]:
    """
    删除文件
    :param access_token:  Access Token
    :param delete_file_list: 删除的文件列表，示例
    :param async_flag:  0 同步，1 自适应，2 异步; 设置async参数为0或2时，则服务端一定会按照同步或异步方式处理，async参数为1时，则服务端按照文件数目自适应选择同步或异步方式，以返回的taskid为准。
    :param api_instance: 自动注入 FilemanagerApi
    :return: FileAsyncManageResult|List[FileSyncManageResultItem]
    """
    file_list = [{'path': tmp} for tmp in delete_file_list]
    # '[{"path":"/test/123456.docx"}]'
    delete_list_str = json.dumps(file_list)
    try:
        api_response = api_instance.filemanagerdelete(access_token, _async=async_flag, filelist=delete_list_str)
        if api_response['errno'] == 0:
            if api_response.get('taskid'):
                return FileAsyncManageResult(taskid=api_response['taskid'])
            return [
                FileSyncManageResultItem(path=http_params_tools.url_decode(tmp_data['path']), errno=tmp_data['errno'])
                for tmp_data in api_response['info']]
        elif api_response['errno'] == -9:
            log_error(logger, f"[BaiduPan]{delete_list_str}delete文件不存在:{api_response}")
        elif api_response['errno'] == 111:
            log_error(logger, f"[BaiduPan]{delete_list_str}delete文件时，有其他异步任务正在执行: {api_response}")
        elif api_response['errno'] == -7:
            log_error(logger, f"[BaiduPan]{delete_list_str}delete文件时，文件名非法:{api_response}")
        else:
            log_error(logger, f"[BaiduPan]{delete_list_str}delete文件失败:{api_response}")
    except openapi_client.ApiException as e:
        log_error(logger, f"[BaiduPan]{delete_list_str}Exception when calling FilemanagerApi->filemanagerdelete", e)


def create_path(access_token, dir_path,
                rename_type: int = 1,
                local_ctime: int = None, local_mtime: int = None,
                mode: int = 1) -> CreatePathResult:
    """
    创建目录
    :param access_token: Access Token
    :param dir_path: 需要创建的目录
    :param rename_type:  文件命名策略，默认0,
                        0 为不重命名，返回冲突;
                        1 为只要path冲突即重命名;
                        2 为path冲突且block_list不同才重命名;
                        3 为覆盖，需要与预上传precreate接口中的rtype保持一致
    :param local_ctime: 客户端创建时间(精确到秒)，默认为当前时间戳，如：1596009229
    :param local_mtime: 客户端修改时间(精确到秒)，默认为当前时间戳, 如：1596009229
    :param mode: 上传方式 1 手动、2 批量上传、3 文件自动备份 4 相册自动备份、5 视频自动备份
    :return: CreatePathResult
    """
    url = "https://pan.baidu.com/rest/2.0/xpan/file?method=create&access_token=" + access_token
    payload = {
        'path': dir_path,
        'isdir': '1',
        'rtype': str(rename_type),
        'local_ctime': local_ctime,
        'local_mtime': local_mtime,
        'mode': mode
    }
    headers = {
        'Host': 'pan.baidu.com'
    }
    try:
        response = requests.request("POST", url, data=payload, headers=headers)
        response.encoding = 'utf-8'
        api_response = response.json()
        if api_response['errno'] == 0:
            return CreatePathResult(**api_response)
        elif api_response['errno'] == -7:
            log_error(logger, f'[BaiduPan]文件或目录名[{dir_path}]错误或无权访问: {api_response}')
        elif api_response['errno'] == -8:
            log_error(logger, f'[BaiduPan]文件或目录[{dir_path}]已存在: {api_response}')
        elif api_response['errno'] == -10:
            log_error(logger, f'[BaiduPan]云端容量已满, path:[{dir_path}]: {api_response}')
        else:
            log_error(logger, f'[BaiduPan]目录[{dir_path}]创建失败: {api_response}')
    except Exception as e:
        log_error(logger, f"[BaiduPan]Exception when create path[{dir_path}]", e)
