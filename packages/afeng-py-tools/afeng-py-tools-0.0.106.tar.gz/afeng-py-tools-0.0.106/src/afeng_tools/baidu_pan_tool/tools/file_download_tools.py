"""
文件下载工具
"""
import math
import os.path
import tempfile
from typing import Generator

import requests

from afeng_tools.baidu_pan_tool.core.baidu_pan_models import FileMetaInfo
from afeng_tools.baidu_pan_tool.tools.file_meta_tools import get_file_metas
from afeng_tools.file_tool import file_tools
from afeng_tools.log_tool.loguru_tools import log_error, get_logger

logger = get_logger()


def _get_split_range_list(file_size: int, block_size: int) -> list[str]:
    """
    拆分列表
    :param file_size: 文件大小
    :param block_size: 每块文件的大小，单位B
    :return: {[start,end]}
    """
    part_num = math.ceil(file_size / block_size)
    part_list = []
    for part_seq in range(0, part_num):
        start_point = part_seq * block_size
        if part_seq < part_num - 1:
            end_point = (part_seq + 1) * block_size - 1
            part_list.append(f'{start_point}-{end_point}')
        else:
            part_list.append(f'{start_point}-')
    return part_list


def _download_bytes(access_token: str, down_link: str, header_range=None) -> bytes:
    """
    下载字节
    :param access_token: Access Token
    :param down_link: DLINK下载地址
    :param header_range: 下载文件指定范围的数据
                如：Range: bytes=0-499表示文件起始的500字节；
                    Range: bytes=500-999表示文件的第二个500字节；
                    Range: bytes=-500 表示文件最后500字节；
                    Range: bytes=500-表示文件500字节以后的范围；
                    Range: bytes=0-0,-1表示文件第一个字节和做后一个字节；
                    Range: bytes=500-600,601-999 表示同时指定多个范围。
    :return: bytes
    """
    headers = {
        'User-Agent': 'pan.baidu.com',
        # 'Host': 'd.pcs.baidu.com'
    }
    if header_range:
        headers['Range'] = header_range
    resp = requests.get(down_link + '&access_token=' + access_token, headers=headers, stream=True)
    if resp.status_code < 400:
        return resp.content
    resp.encoding = 'utf-8'
    log_error(logger, f'[BiaduPan]文件下载失败，下载链接没有能下载，响应码是：{resp.status_code}, 响应内容是：{resp.text}')


def _get_downloaded_file(fs_id: int) -> str:
    """获取下载配置文件"""
    tmp_path = tempfile.gettempdir()
    save_path = os.path.join(tmp_path, 'BaiduPan')
    os.makedirs(save_path, exist_ok=True)
    return os.path.join(save_path, f'{fs_id}.download')


def _read_downloaded_range(fs_id: int) -> list[str]:
    """读取已经下载的分片范围列表（当断点续传时），"""
    downloaded_file = _get_downloaded_file(fs_id)
    logger.info(f'[BiaduPan]文件下载，分片信息保存在[{downloaded_file}]')
    if os.path.exists(downloaded_file):
        return file_tools.read_file_lines(downloaded_file)


def _save_downloaded_range(fs_id: int, tmp_range):
    """保存已经下载的分片信息"""
    with open(_get_downloaded_file(fs_id), 'a', encoding='utf-8') as fd:
        fd.write(tmp_range + '\n')


def _delete_downloaded_range_file(fs_id: int):
    """删除下载进度存储文件"""
    os.remove(_get_downloaded_file(fs_id))


def download_bytes(access_token: str, file_meta: FileMetaInfo,
                   max_size: int = 50 * 1000 * 1000,
                   block_size: int = 5 * 1000 * 1000) -> Generator[dict[int, bytes], None, None]:
    """
    下载字节
    :param access_token: Access Token
    :param file_meta: 文件元数据
    :param max_size: 不分片下载的最大大小，默认50M
    :param block_size: 分片的大小, 默认5M
    :return: (开始位置,bytes)
    """
    down_link = file_meta.dlink
    file_size = file_meta.size
    if file_size <= max_size:
        logger.info(f'[BaiduPan]下载文件[{file_meta.path}]')
        yield 0, _download_bytes(access_token=access_token, down_link=down_link)
    else:
        # 分片下载
        split_range_list = _get_split_range_list(file_size, block_size)
        # 读取已经下载的分片
        downloaded_range_list = _read_downloaded_range(file_meta.fs_id)
        for tmp_range in split_range_list:
            if downloaded_range_list and tmp_range in downloaded_range_list:
                continue
            logger.info(f'[BaiduPan]下载文件[{file_meta.path}]-[{tmp_range}]')
            yield int(tmp_range.split('-')[0]), _download_bytes(access_token=access_token, down_link=down_link,
                                                                header_range=f'bytes={tmp_range}')
            _save_downloaded_range(file_meta.fs_id, tmp_range)
        # 删除分片记录文件
        _delete_downloaded_range_file(file_meta.fs_id)


def download_file(access_token: str, fs_id: int, save_path: str,
                  save_file_name: str = None,
                  max_size=5 * 1000 * 1000, block_size=1 * 1000 * 1000) -> str:
    """
    下载文件
    :param access_token: Access Token
    :param fs_id: 文件在云端的唯一标识ID
    :param save_path: 文件的保存路径
    :param save_file_name: 保存的文件名，如果为None，则使用原有文件名
    :param max_size: 不分片下载的最大大小，默认5M
    :param block_size: 分片的大小, 默认1M
    :return: 文件绝对路径
    """
    file_meta_list = get_file_metas(access_token=access_token, fs_id_list=[fs_id], d_link=1)
    if file_meta_list:
        file_meta = file_meta_list[0]
        download_generator = download_bytes(access_token=access_token, file_meta=file_meta,
                                            max_size=max_size, block_size=block_size)
        save_file = os.path.join(save_path, save_file_name if save_file_name else file_meta.filename)
        for start, content in download_generator:
            with open(save_file, 'ab') as f:
                f.seek(start)
                f.write(content)
        logger.info(f'[BaiduPan][{fs_id}]-[{file_meta.path}]下载存储完成，存储文件为:{save_file}')
        return save_file


def get_download_url(access_token: str, fs_id: int) -> str:
    file_meta_list = get_file_metas(access_token=access_token, fs_id_list=[fs_id], d_link=1)
    if file_meta_list:
        file_meta = file_meta_list[0]
        return f'{file_meta.dlink}&access_token={access_token}'
