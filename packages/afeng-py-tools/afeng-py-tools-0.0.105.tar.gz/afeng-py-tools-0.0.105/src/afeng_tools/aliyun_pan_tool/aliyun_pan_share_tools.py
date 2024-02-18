"""
阿里云盘分享工具 pip install aligo -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
"""
import os
from typing import List, Callable

from aligo import Aligo, BaseShareFile, GetShareTokenResponse, ShareLinkExtractCodeResponse, \
    BatchShareFileSaveToDriveResponse

from afeng_tools.encryption_tool import hashlib_tools
from afeng_tools.file_tool.tmp_file_tools import get_user_tmp_dir
from afeng_tools.serialization_tool import pickle_tools


def get_share_info_by_link(ali_api: Aligo, share_msg: str) -> ShareLinkExtractCodeResponse:
    """
    通过链接获取分享信息
    :param ali_api: Aligo
    :param share_msg: 分享信息
                如：「心灵奇旅 4K 原盘 REMUX」https://www.aliyundrive.com/s/FYoddEbsSwV
                如： https://www.aliyundrive.com/s/LkUS6BrconT/folder/62074d95b39e519f60be4f73b68ac493e9977a90
    :return: 分享信息，如：result.share_id, result.share_pwd
    """
    return ali_api.share_link_extract_code(share_msg)


def get_share_token(ali_api: Aligo, share_id: str, share_pwd: str = '') -> GetShareTokenResponse:
    """获取share_token"""
    return ali_api.get_share_token(share_id, share_pwd=share_pwd)


def list_share_root_files(ali_api: Aligo, share_token: GetShareTokenResponse) -> List[BaseShareFile]:
    """
    列出分享根路径中的文件
    :param ali_api: Aligo
    :param share_token: 可以调用 get_share_token() 方法获取
    :return: List[BaseShareFile]
    """
    return ali_api.get_share_file_list(share_token)


def list_share_path_files(ali_api: Aligo, share_token: GetShareTokenResponse,
                          parent_file_id='root') -> List[BaseShareFile]:
    """
    列出分享根路径中的文件
    :param ali_api: Aligo
    :param share_token: 可以调用 get_share_token() 方法获取
    :param parent_file_id: parent_file_id
    :return: List[BaseShareFile]
    """
    return ali_api.get_share_file_list(share_token, parent_file_id=parent_file_id)


def _tree_share(ali_api: Aligo, share_token: GetShareTokenResponse,
                parent_file_id: str = 'root', parent_path: str = None,
                root_cache_path: str = None,
                callback_func: Callable = None) -> List[tuple[str, BaseShareFile]]:
    """
    树形递归获取分享文件
    :param ali_api:  Aligo
    :param share_token: 可以调用 get_share_token() 方法获取
    :param parent_file_id: parent_file_id
    :param parent_path: parent_path
    :param root_cache_path: 当是内部递归调用时，传入缓存的根路径
    :param callback_func: 获取到文件信息后的回调函数, 有两个参数：pan_path:str, pan_file:BaseShareFile
    :return: [(路径,BaseShareFile)]
    """
    try:
        file_list = ali_api.get_share_file_list(share_token, parent_file_id=parent_file_id)
    except KeyError as e:
        share_token = get_share_token(ali_api, share_token.share_id, share_token.share_pwd)
        file_list = ali_api.get_share_file_list(share_token, parent_file_id=parent_file_id)
    if file_list:
        all_files = []
        is_root: bool = False
        if root_cache_path is None:
            is_root = True
            root_cache_path = os.path.join(get_user_tmp_dir(), hashlib_tools.calc_md5(share_token.share_id))
            os.makedirs(root_cache_path, exist_ok=True)
        for tmp_file in file_list:
            pan_path = parent_path + '/' + tmp_file.name if parent_path else tmp_file.name
            print(f'[{tmp_file.type}]{pan_path}')
            if tmp_file.type == 'folder':
                tmp_cache = os.path.join(root_cache_path, tmp_file.file_id)
                if os.path.exists(tmp_cache):
                    child_list = pickle_tools.parse_to_obj(tmp_cache)
                    if child_list and callback_func and isinstance(callback_func, Callable):
                        for temp_child_file_name, temp_child_file in child_list:
                            callback_func(temp_child_file_name, temp_child_file)
                else:
                    child_list = _tree_share(ali_api, share_token,
                                             parent_file_id=tmp_file.file_id,
                                             parent_path=pan_path, root_cache_path=root_cache_path,
                                             callback_func=callback_func)
                if child_list:
                    all_files.extend(child_list)
                    if not os.path.exists(tmp_cache):
                        pickle_tools.save_to_file(child_list, tmp_cache)
            else:
                all_files.append((pan_path, tmp_file))
                if callback_func and isinstance(callback_func, Callable):
                    if callback_func and isinstance(callback_func, Callable):
                        callback_func(pan_path, tmp_file)
        if is_root:
            # 先注释了删除
            # shutil.rmtree(root_cache_path)
            pass
        return all_files


def list_share_all_file(ali_api: Aligo, share_token: GetShareTokenResponse,
                        parent_file_id='root', parent_path: str = None,
                        callback_func: Callable = None) -> List[tuple[str, BaseShareFile]]:
    """
    递归遍历文件
    :param ali_api: Aligo
    :param share_token: 可以调用 get_share_token() 方法获取
    :param parent_file_id: 父 file_id
    :param parent_path: 父路径
    :param callback_func: 获取到文件信息后的回调函数, 有两个参数：pan_path:str, pan_file:BaseShareFile
    :return: [(路径,BaseShareFile)]
    """
    return _tree_share(ali_api, share_token, parent_file_id=parent_file_id, parent_path=parent_path,
                       callback_func=callback_func)


def save_share_file_to_pan(ali_api: Aligo,
                           share_token: GetShareTokenResponse) -> List[BatchShareFileSaveToDriveResponse]:
    """
    保存所有分享文件到云盘
    :param ali_api: Aligo
    :param share_token: 可以调用 get_share_token() 方法获取
    :return: List[BatchShareFileSaveToDriveResponse]
    """
    # 如果遇到分享文件非常多，此段代码运行完成后，不会立马看到所有文件，可能需要几个小时才能陆续保存完成
    # 在网页保存需要几个小时，用这个一下就可以了，阿里云服务器会处理，不用等待
    return ali_api.share_file_save_all_to_drive(share_token)


def download_share_file(ali_api: Aligo, share_token: GetShareTokenResponse, local_save_path: str,
                        download_before_callback: Callable[[str, BaseShareFile], bool] = None,
                        download_after_callback: Callable[[str, BaseShareFile, str], bool] = None):
    """
    下载分享中的文件到本地
    :param ali_api: Aligo
    :param share_token: 可以调用 get_share_token() 方法获取
    :param local_save_path: 本地存储路径
    :param download_before_callback: lambda pan_path,share_file: True
    :param download_after_callback: lambda pan_path,share_file,local_file: True
    :return:
    """
    for tmp_pan_path, tmp_file in list_share_all_file(ali_api, share_token):
        download_flag = True
        if download_before_callback and isinstance(download_before_callback, Callable):
            download_flag = download_before_callback(tmp_pan_path, tmp_file)
        if download_flag:
            download_file = ali_api.get_share_link_download_url(tmp_file.file_id, share_token)
            local_file = ali_api.download_file(file_path=local_save_path,
                                               url=download_file.download_url or download_file.url)
            if download_after_callback and isinstance(download_after_callback, Callable):
                download_after_callback(tmp_pan_path, tmp_file, local_file)


def cancel_share(ali_api: Aligo, share_id: str):
    """取消分享"""
    ali_api.cancel_share(share_id)


def create_aligo_share(ali_api: Aligo, file_id: str) -> str:
    """创建Aligo分享"""
    return ali_api.share_folder_by_aligo(file_id)


def save_aligo_share(ali_api: Aligo, aligo_share_data: str) -> list:
    """保存Aligo分享"""
    return ali_api.save_files_by_aligo(aligo_share_data)
