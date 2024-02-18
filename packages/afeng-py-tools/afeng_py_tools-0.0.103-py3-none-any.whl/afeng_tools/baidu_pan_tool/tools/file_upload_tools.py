"""
文件上传工具
"""
import json
import math
import os
import tempfile
from typing import Literal

import requests
import typing_extensions

import openapi_client
from openapi_client.api.fileupload_api import FileuploadApi
from afeng_tools.encryption_tool import hashlib_tools
from afeng_tools.baidu_pan_tool.core.baidu_pan_decorator_tools import auto_file_upload_api
from afeng_tools.baidu_pan_tool.core.baidu_pan_models import PreCreateResult, SplitUploadResult, UploadCreateResult, \
    SplitUploadTempInfo
from afeng_tools.file_tool import file_tools
from afeng_tools.http_tool import http_params_tools
from afeng_tools.log_tool.loguru_tools import get_logger, log_error

logger = get_logger()


def _get_upload_config_file(file_id: str) -> str:
    """获取上传配置文件"""
    tmp_path = tempfile.gettempdir()
    save_path = os.path.join(tmp_path, 'BaiduPan')
    os.makedirs(save_path, exist_ok=True)
    return os.path.join(save_path, f'{file_id}.upload')


def _read_upload_config_range(file_id: str) -> SplitUploadTempInfo:
    """读取已经上传的分片范围列表（当断点续传时），"""
    downloaded_file = _get_upload_config_file(file_id)
    logger.info(f'[BiaduPan]文件分片上传，分片信息保存在[{downloaded_file}]')
    if os.path.exists(downloaded_file):
        return SplitUploadTempInfo.model_validate_json(file_tools.read_file(downloaded_file))


def _save_upload_config_range(file_id: str, temp_upload_info: SplitUploadTempInfo):
    """保存已经上传的分片信息"""
    file_tools.save_file(temp_upload_info.model_dump_json(), _get_upload_config_file(file_id))


def _delete_upload_config_range_file(file_id: str):
    """删除上传进度存储文件"""
    os.remove(_get_upload_config_file(file_id))


@auto_file_upload_api
def _upload_pre_create(access_token: str, pan_path: str, size: int, is_dir: bool,
                       block_list: list[str], rtype: Literal[1, 2, 3] | int = 2,
                       api_instance: FileuploadApi = None) -> PreCreateResult:
    """
    预上传：预上传是通知网盘云端新建一个上传任务，网盘云端返回唯一ID uploadid 来标识此上传任务。
    :param access_token: Access Token
    :param pan_path: 传后使用的文件绝对路径，如：/apps/appName/filename.jpg
            对于一般的第三方软件应用，路径以 "/apps/your-app-name/" 开头。对于小度等硬件应用，路径一般 "/来自：小度设备/" 开头。对于定制化配置的硬件应用，根据配置情况进行填写。
    :param size: 文件和目录两种情况：上传文件时，表示文件的大小，单位B；上传目录时，表示目录的大小，目录的话大小默认为0
    :param is_dir: 是否为目录，0 文件，1 目录
    :param block_list: 文件各分片MD5数组的json串。
                    block_list的含义如下:
                        如果上传的文件小于4MB，其md5值（32位小写）即为block_list字符串数组的唯一元素；
                        如果上传的文件大于4MB，需要将上传的文件按照4MB大小在本地切分成分片，不足4MB的分片自动成为最后一个分片，所有分片的md5值（32位小写）组成的字符串数组即为block_list。
    :param rtype: 文件命名策略。
                    1 表示当path冲突时，进行重命名
                    2 表示当path冲突且block_list不同时，进行重命名
                    3 当云端存在同名文件时，对该文件进行覆盖
    :param api_instance: 自动注入 FileuploadApi
    :return: PreCreateResult
    """
    try:
        block_list_str = json.dumps(block_list)
        api_response = api_instance.xpanfileprecreate(access_token, path=pan_path, isdir=1 if is_dir else 0,
                                                      size=size, block_list=block_list_str,
                                                      autoinit=1, rtype=rtype)
        logger.info(f"[BaiduPan]upload_pre_create[{pan_path}]:[{api_response}]")
        return PreCreateResult(**api_response)
    except openapi_client.ApiException as e:
        log_error(logger, f"[BaiduPan]upload_pre_create[{pan_path}]出现异常", e)


def _get_part_info_list(file_size: int) -> list[tuple[int, int]]:
    """
    获取分页信息列表
    :param file_size:
    :return: [(开始位置,读取长度)]
    """
    block_size = 4 * 1024 * 1024
    # 如果上传的文件大于4MB，需要将上传的文件按照4MB大小在本地切分成分片，不足4MB的分片自动成为最后一个分片，所有分片的md5值（32位小写）组成的字符串数组即为block_list。
    part_info_list = []
    part_num = math.ceil(file_size / block_size)
    for i in range(part_num):
        start_index = i * block_size
        part_info_list.append((start_index, block_size if i < part_num - 1 else file_size - start_index))
    return part_info_list


def _get_block_list(local_file: str, part_info_list: list[tuple[int, int]]) -> list[str]:
    """获取文件的block_list"""
    block_list = []
    with open(local_file, 'rb') as tmp_file:
        for tmp_start, tmp_length in part_info_list:
            tmp_file.seek(tmp_start)
            part_body = tmp_file.read(tmp_length)
            block_list.append(hashlib_tools.calc_byte_md5(part_body))
    return block_list


@auto_file_upload_api
def _split_upload(access_token: str, pan_path: str, upload_id: str, part_seq: int, body: bytes,
                  api_instance: FileuploadApi = None) -> SplitUploadResult:
    """
    分片上传：本接口用于将本地文件上传到网盘云端服务器。
    :param access_token: Accesss Token
    :param pan_path: 上传后使用的文件绝对路径
    :param upload_id: 上一个阶段预上传precreate接口下发的uploadid
    :param part_seq: 文件分片的位置序号，从0开始，参考上一个阶段预上传precreate接口返回的block_list
    :param body: 上传的文件内容
    :param api_instance:
    :return:
    """
    temp_file = os.path.join(tempfile.gettempdir(), f'{upload_id}.tmp')
    try:
        file_tools.save_file(body, temp_file, binary_flag=True)
        api_response = api_instance.pcssuperfile2(access_token, partseq=str(part_seq), path=pan_path,
                                                  uploadid=upload_id, type='tmpfile',
                                                  file=open(temp_file, 'rb'))
        logger.info(f"[BaiduPan]split_upload[{pan_path}]-[{part_seq}]:[{api_response}]")
        return SplitUploadResult(**api_response)
    except openapi_client.ApiException as e:
        log_error(logger, f"[BaiduPan]split_upload[{pan_path}]-[{part_seq}]出现异常", e)
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


@auto_file_upload_api
def _upload_create(access_token: str, pan_path: str, is_dir: bool, size: int,
                   upload_id: str, block_list: list[str], rtype: Literal[1, 2, 3] | int = 2,
                   api_instance: FileuploadApi = None) -> UploadCreateResult:
    """
    分片上传的第三步：创建文件，本接口用于将多个文件分片合并成一个文件，生成文件基本信息，完成文件的上传最后一步。
    :param access_token: Access Token
    :param pan_path: 上传后使用的文件绝对路径，需要与预上传precreate接口中的path保持一致
    :param is_dir: 是否目录，0 文件、1 目录，需要与预上传precreate接口中的isdir保持一致
    :param size: 文件或目录的大小，必须要和文件真实大小保持一致，需要与预上传precreate接口中的size保持一致
    :param upload_id: 预上传precreate接口下发的uploadid
    :param block_list: 文件各分片md5数组的json串
    :param rtype: 文件命名策略，默认1
                    0 为不重命名，返回冲突
                    1 为只要path冲突即重命名
                    2 为path冲突且block_list不同才重命名
                    3 为覆盖，需要与预上传precreate接口中的rtype保持一致
    :param api_instance: 自动注入FileuploadApi
    :return: UploadCreateResult
    """
    try:
        block_list_str = json.dumps(block_list)
        api_response = api_instance.xpanfilecreate(access_token, path=pan_path, isdir=1 if is_dir else 0,
                                                   size=size, uploadid=upload_id,
                                                   block_list=block_list_str, rtype=rtype)
        logger.info(f"[BaiduPan]upload_create[{pan_path}]:[{api_response}]")
        if api_response['errno'] == 0:
            return UploadCreateResult(**api_response)
        elif api_response['errno'] == -7:
            log_error(logger, f"[BaiduPan]文件或目录名错误或无权访问, upload_path:{pan_path}\n{api_response}")
        elif api_response['errno'] == -8:
            log_error(logger, f"[BaiduPan]文件或目录已存在, upload_path:{pan_path}\n{api_response}")
        elif api_response['errno'] == -10:
            log_error(logger, f"[BaiduPan]云端容量已满, upload_path:{pan_path}\n{api_response}")
        elif api_response['errno'] == 10:
            log_error(logger, f"[BaiduPan]创建文件失败, upload_path:{pan_path}\n{api_response}")
        elif api_response['errno'] == 31190:
            log_error(logger, f"[BaiduPan]文件不存在, upload_path:{pan_path}\n{api_response}")
        elif api_response['errno'] == 31365:
            log_error(logger, f"[BaiduPan]文件总大小超限, upload_path:{pan_path}\n{api_response}")
        else:
            log_error(logger, f"[BaiduPan]创建文件失败, upload_path:{pan_path}\n{api_response}")
    except openapi_client.ApiException as e:
        log_error(logger, f"[BaiduPan]创建文件失败出现异常, upload_path:{pan_path}", e)


def upload_file(access_token: str, local_file: str, pan_path: str,
                rtype: Literal[1, 2, 3] | int = 2) -> UploadCreateResult | None:
    """
    上传文件到百度网盘
    :param access_token: Access Token
    :param local_file: 本地文件
    :param pan_path: 网盘路径
    :param rtype: 文件命名策略，默认1
                    0 为不重命名，返回冲突
                    1 为只要path冲突即重命名
                    2 为path冲突且block_list不同才重命名
                    3 为覆盖，需要与预上传precreate接口中的rtype保持一致
    :return: UploadCreateResult
    """
    file_id = hashlib_tools.calc_md5(f'{local_file}|{pan_path}')
    # 读取上传临时文件
    upload_temp_info = _read_upload_config_range(file_id)
    if not upload_temp_info:
        # 1、预上传
        file_size = 0 if os.path.isdir(local_file) else os.path.getsize(local_file)
        is_dir = os.path.isdir(local_file)
        part_info_list = _get_part_info_list(file_size)
        block_list = _get_block_list(local_file, part_info_list)
        pre_create_result = _upload_pre_create(access_token, pan_path, size=file_size, is_dir=is_dir,
                                               block_list=block_list, rtype=rtype)
        if pre_create_result.errno != 0:
            return
        upload_temp_info = SplitUploadTempInfo(file_size=file_size, is_dir=is_dir,
                                               part_info_list=part_info_list, upload_id=pre_create_result.uploadid,
                                               block_list=block_list)
        _save_upload_config_range(file_id, upload_temp_info)
    # 2、分片上传
    for index, (tmp_start, tmp_length) in enumerate(upload_temp_info.part_info_list):
        if upload_temp_info.uploaded_part_list and (tmp_start, tmp_length) in upload_temp_info.uploaded_part_list:
            continue
        split_upload_result = _split_upload(access_token, pan_path,
                                            upload_id=upload_temp_info.upload_id, part_seq=index,
                                            body=file_tools.read_file_body(local_file,
                                                                           start=tmp_start, length=tmp_length))
        if split_upload_result.md5 is None:
            return
        upload_temp_info.uploaded_part_list.append((tmp_start, tmp_length))
        _save_upload_config_range(file_id, upload_temp_info)
    # 3、创建文件
    upload_create_result = _upload_create(access_token, pan_path, is_dir=upload_temp_info.is_dir,
                                          size=upload_temp_info.file_size, upload_id=upload_temp_info.upload_id,
                                          block_list=upload_temp_info.block_list, rtype=rtype)
    # 删除上传临时存储文件
    _delete_upload_config_range_file(file_id)
    if upload_create_result.errno != 0:
        return
    return upload_create_result


@typing_extensions.deprecated('请使用upload_file(), 当前接口测试上传时没有成功，'
                              '出现{"error_code":31064,"error_msg":"file is not authorized"}')
def post_upload_file(access_token: str, local_file: str, pan_path: str,
                     on_dup: Literal['fail', 'overwrite', 'newcopy'] | str = 'newcopy') -> UploadCreateResult:
    """
    单步上传：本接口用于实现小文件单步上传一次HTTP请求交互即可完成上传的场景。
    :param access_token: Access Token
    :param local_file: 需要上传的本地文件
    :param pan_path: 上传的文件绝对路径
    :param on_dup: 上传的文件绝对路径冲突时的策略。fail（默认：冲突时失败）overwrite（冲突时覆盖） newcopy（冲突时重命名
    :return:
    """
    params = {
        'method': 'upload',
        'access_token': access_token,
        'path': http_params_tools.url_encode(pan_path),
        'ondup': on_dup
    }
    files = [
        ('file', open(local_file, 'rb'))
    ]
    headers = {'Host': 'pan.baidu.com'}
    post_url = 'https://d.pcs.baidu.com/rest/2.0/pcs/file?' + http_params_tools.url_encode_params(params)
    print(post_url)
    try:
        response = requests.post(post_url, headers=headers, files=files)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            api_response = response.json()
            logger.info(f"[BaiduPan]post_upload_file[{local_file}]-[{pan_path}]:[{api_response}]")
            return UploadCreateResult(**api_response)
        else:
            log_error(logger,
                      f'[BaiduPan][{local_file}]-[{pan_path}]单步上传失败: {response.status_code}-{response.text}')
    except Exception as e:
        log_error(logger, f'[BaiduPan][{local_file}]-[{pan_path}]单步上传失败', e)
