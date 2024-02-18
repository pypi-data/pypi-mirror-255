"""
下载工具
    安装：pip install certifi -i https://pypi.tuna.tsinghua.edu.cn/simple/  -U
         pip install requests -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
         pip install tqdm -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
"""
import os
from typing import Optional

import certifi
import requests
from tqdm.asyncio import tqdm

from afeng_tools.http_tool.decorator.http_auto_retry_tools import auto_retry
from afeng_tools.log_tool.loguru_tools import get_logger, log_error

logger = get_logger()

DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.24'


@auto_retry(max_retries=3)
def download_chunk_file(download_url: str, save_path: str, save_file_name=None, chunk_size: int = 1024,
                        params: Optional[dict] = None, headers: Optional[dict] = None) -> str:
    """
    分块断点续传下载
    :param download_url: 下载url
    :param save_path: 本地保存路径
    :param save_file_name: 保存文件名
    :param chunk_size: 每块大小
    :param params: 请求参数
    :param headers: 请求头
    :return: 本地保存的文件路径
    """
    if headers is None:
        headers = {
            "User-Agent": DEFAULT_USER_AGENT
        }
    if 'User-Agent' not in headers:
        headers['User-Agent'] = DEFAULT_USER_AGENT
    verify = False
    if download_url.startswith('https'):
        verify = certifi.where()
    response = requests.get(download_url, params=params, headers=headers, stream=True, verify=verify, timeout=(10, 20))
    # 记录下载文件的大小
    total_length = int(response.headers.get('content-length', 0))
    if total_length == 0:
        return download_file(download_url=download_url, save_path=save_path, save_file_name=save_file_name,
                             params=params, headers=headers)
    # 保存文件名
    if not save_file_name:
        save_file_name = download_url.rsplit('/', maxsplit=1)[-1].split('?', maxsplit=1)[0]
    os.makedirs(save_path, exist_ok=True)
    # 保存文件路径
    save_file = os.path.join(save_path, save_file_name)
    # 临时下载文件
    down_tmp_file = save_file + '.down-tmp'
    # 本地已经下载的文件大小
    down_size = 0
    if os.path.exists(save_file):
        down_size = os.path.getsize(save_file)
    elif os.path.exists(down_tmp_file):
        down_size = os.path.getsize(down_tmp_file)
    if down_size >= total_length:
        logger.info(f'The file has been downloaded to the local, down_url[{download_url}]')
        return save_file
    else:
        headers['Range'] = f'bytes={down_size}-{total_length}'
        logger.info(f'[begin-download][{total_length}-{down_size}]:[{download_url}]')
        response = requests.get(download_url, params=params, headers=headers, stream=True, verify=verify,
                                timeout=(10, 20))

        # 记录下载文件的大小
        with open(down_tmp_file, 'ab') as fd, tqdm(initial=down_size, desc="正在下载", total=total_length,
                                                   unit='B', unit_scale=True, unit_divisor=1024) as bar:
            # 指针移到末尾
            fd.seek(down_size)
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    size = fd.write(chunk)
                    fd.flush()
                    bar.update(size)
        os.rename(down_tmp_file, save_file)
        return save_file


@auto_retry(max_retries=3)
def download_file(download_url, save_path: str, save_file_name=None, buffer_size: int = 1024,
                  params: Optional[dict] = None, headers: Optional[dict] = None):
    """
    下载文件(不支持断点续传，只能一次性下载完)
    :param download_url: 文件url
    :param save_path: 文件本地保存路径
    :param save_file_name: 保存文件名
    :param buffer_size: 流读取，每次读取大小
    :param params: 请求参数
    :param headers: 请求头
    :return: 下载成功后，返回本地保存文件路径;下载失败后，返回None
    """
    if headers is None:
        headers = {
            "User-Agent": DEFAULT_USER_AGENT
        }
    if 'User-Agent' not in headers:
        headers[
            'User-Agent'] = DEFAULT_USER_AGENT
    verify = False
    if download_url.startswith('https'):
        verify = certifi.where()
    # 请求结果
    response = requests.get(download_url, params=params, headers=headers, stream=True, verify=verify, timeout=(10, 20))
    if response.status_code == 200:
        # 记录下载文件的大小
        total_length = int(response.headers.get('content-length', 0))
        # 保存文件名
        if not save_file_name:
            save_file_name = download_url.rsplit('/', maxsplit=1)[-1].split('?', maxsplit=1)[0]
        os.makedirs(save_path, exist_ok=True)
        # 保存文件路径
        save_file = os.path.join(save_path, save_file_name)
        # 临时下载文件
        down_tmp_file = save_file + '.down-tmp'
        if os.path.exists(save_file):
            logger.info(f'The file has been downloaded to the local, down_url[{download_url}]')
        else:
            # 记录下载文件的大小
            with open(down_tmp_file, 'ab') as fd, tqdm(initial=0, desc="正在下载", total=total_length,
                                                       unit='B', unit_scale=True, unit_divisor=1024) as bar:
                for chunk in response.iter_content(chunk_size=buffer_size):
                    if chunk:
                        size = fd.write(chunk)
                        fd.flush()
                        bar.update(size)
            os.rename(down_tmp_file, save_file)
            return save_file
    else:
        response.encoding = 'utf-8'
        log_error(logger, f'文件下载失败！[{download_url}]：错误信息[{response.status_code}]{response.text}')

# TODO 多线程下载
