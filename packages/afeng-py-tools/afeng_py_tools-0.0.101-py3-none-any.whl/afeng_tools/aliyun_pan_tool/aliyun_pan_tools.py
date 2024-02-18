"""
阿里云盘工具 pip install aligo -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
"""
import os
from typing import List, Callable

from aligo import Aligo, BaseUser, BaseFile, EMailConfig, set_config_folder, CreateFileResponse, GetFileRequest
from aligo.types.Enum import CheckNameMode

from afeng_tools.encryption_tool import hashlib_tools
from afeng_tools.file_tool.tmp_file_tools import get_user_tmp_dir
from afeng_tools.serialization_tool import pickle_tools


def get_ali_api_by_email(receive_email: str, send_email: str, send_password: str, email_host: str,
                         email_port: int) -> Aligo:
    """
    获取api接口：发送登录二维码到邮箱(建议将邮箱绑定到微信，这样能实时收到提醒，登录过期后也可以第一时间收到登录请求。)
    :param receive_email:  接收登录邮件的邮箱地址
    :param send_email: 发送邮件的邮箱
    :param send_password: 发送邮件的密码
    :param email_host: 发送邮件的主机
    :param email_port: 发送邮件的端口
    :return: Aligo
    """
    email_config = EMailConfig(
        email=receive_email,
        # 自配邮箱
        user=send_email,
        password=send_password,
        host=email_host,
        port=email_port,
    )
    return Aligo(email=email_config)


def get_ali_api_by_web(port: int, use_aria2: bool = False) -> Aligo:
    """获取api接口：打开浏览器访问 http://<YOUR_IP>:<port> 网页扫码登录"""
    return Aligo(port=port, use_aria2=use_aria2)


def get_ali_api(name: str = None, config_path: str = None, use_aria2: bool = False) -> Aligo:
    """
    获取api接口：第一次使用，会弹出二维码，供扫描登录
    :param name: 配置文件名，如：name='一号服务器'， 会创建 <用户目录>/.alig/一号服务器.json 配置文件
    :param config_path: 配置文件目录，默认是 <用户目录>/.alig
    :param use_aria2: 是否使用 aria2 下载
    :return:
    """
    if config_path:
        set_config_folder(config_path)
    if name:
        return Aligo(name=name, use_aria2=use_aria2)
    return Aligo(use_aria2=use_aria2)


def get_user_info(ali_api: Aligo) -> BaseUser:
    """获取用户信息"""
    return ali_api.get_user()


def list_file(ali_api: Aligo, parent_file_id: str = 'root') -> List[BaseFile]:
    """列出路径下的文件"""
    return ali_api.get_file_list(parent_file_id=parent_file_id)


def list_path(ali_api: Aligo, pan_path: str) -> List[BaseFile] | None:
    """列出路径下的文件"""
    pan_file = get_file_info(ali_api, pan_path)
    if pan_file:
        return list_file(ali_api, parent_file_id=pan_file.file_id)


def list_all_file(ali_api: Aligo, pan_path: str,
                  root_cache_path: str = None, callback_func: Callable = None) -> list[tuple[str, BaseFile]]:
    """
    递归列出目录下文件
    :param ali_api: Aligo
    :param pan_path: 要递归列出的网盘路径
    :param root_cache_path: 当是内部递归调用时，传入缓存的根路径
    :param callback_func: 获取到文件信息后的回调函数, 有两个参数：pan_path:str, pan_file:BaseFile
    :return: list[tuple[文件路径, BaseFile]]
    """
    ali_file_list = list_path(ali_api, pan_path)
    if ali_file_list:
        file_list = []
        is_root: bool = False
        if root_cache_path is None:
            is_root = True
            root_cache_path = os.path.join(get_user_tmp_dir(), hashlib_tools.calc_md5(pan_path))
            os.makedirs(root_cache_path, exist_ok=True)
        for tmp in ali_file_list:
            tmp_file_name = pan_path + '/' + tmp.name
            print(f'[{tmp.type}]{tmp_file_name}')
            if tmp.type == 'folder':
                tmp_cache = os.path.join(root_cache_path, tmp.file_id)
                if os.path.exists(tmp_cache):
                    child_list = pickle_tools.parse_to_obj(tmp_cache)
                    if child_list and callback_func and isinstance(callback_func, Callable):
                        for temp_child_file_name, temp_child_file in child_list:
                            callback_func(temp_child_file_name, temp_child_file)
                else:
                    child_list = list_all_file(ali_api, tmp_file_name,
                                               root_cache_path=root_cache_path,
                                               callback_func=callback_func)
                if child_list:
                    file_list.extend(child_list)
                    if not os.path.exists(tmp_cache):
                        pickle_tools.save_to_file(child_list, tmp_cache)
            else:
                file_list.append((tmp_file_name, tmp))
                if callback_func and isinstance(callback_func, Callable):
                    callback_func(tmp_file_name, tmp)
        if is_root:
            # 先注释了删除
            # shutil.rmtree(root_cache_path)
            pass
        return file_list


def get_file_info(ali_api: Aligo, pan_path: str, parent_file_id: str = 'root') -> BaseFile | None:
    """
    通过文件路径获取文件信息
    :param ali_api: Aligo
    :param pan_path: 网盘文件路径
    :param parent_file_id: 父id
    :return: 文件基础信息
    """
    pan_path = pan_path.strip('/')
    path_list = pan_path.split('/')
    if len(path_list) == 1:
        for tmp in list_file(ali_api, parent_file_id=parent_file_id):
            if tmp.name == path_list[0]:
                return tmp
        return
    else:
        parent_folder = ali_api.get_folder_by_path('/'.join(path_list[0:-1]), parent_file_id=parent_file_id,
                                                   create_folder=False)
        if parent_folder:
            parent_file_id = parent_folder.file_id
            folder = ali_api.get_folder_by_path(path_list[-1], parent_file_id=parent_file_id, create_folder=False)
            if folder:
                return folder
            file_list = ali_api.get_file_list(parent_file_id=parent_file_id, type='file')
            for file in file_list:
                if path_list[-1] == file.name:
                    return file


def get_file_by_id(ali_api: Aligo, file_id: str, drive_id: str = None) -> BaseFile:
    """
    通过文件id获取文件信息
    :param ali_api: Aligo
    :param file_id: 文件id
    :param drive_id: Optional[str] 指定网盘id, 默认为 None
    :return: 文件基础信息
    """
    return ali_api._core_get_file(GetFileRequest(file_id=file_id, drive_id=drive_id))


def create_folder(ali_api: Aligo, name: str, parent_file_id: str = 'root', drive_id: str = None,
                  check_name_mode: CheckNameMode = 'auto_rename') -> CreateFileResponse:
    """
    创建文件夹
    :param ali_api: Aligo
    :param name: [str] 文件夹名
    :param parent_file_id: Optional[str] 父文件夹id, 默认为 'root'
    :param drive_id: Optional[str] 指定网盘id, 默认为 None
    :param check_name_mode: Optional[CheckNameMode] 检查文件名模式, 默认为 'auto_rename'
    :return: [CreateFileResponse]
    """
    return ali_api.create_folder(name=name, parent_file_id=parent_file_id, drive_id=drive_id,
                                 check_name_mode=check_name_mode)


def upload_files(ali_api: Aligo, local_file_paths: List[str], pan_path: str = None, drive_id: str = None,
                 check_name_mode: CheckNameMode = "auto_rename") -> List[BaseFile]:
    """
    批量上传文件
    :param ali_api: Aligo
    :param local_file_paths: [List[str]] 文件路径列表, 如：['/Users/aligo/Desktop/test1.txt', '/Users/aligo/Desktop/test2.txt']
    :param pan_path: 上传到的网盘路径, 如：'我的资源/1080p'
    :param drive_id: Optional[str] 指定网盘id, 默认为 None
    :param check_name_mode: Optional[CheckNameMode] 检查文件名模式, 默认为 'auto_rename'
    :return: [List[BaseFile]]
    """
    if pan_path is None:
        parent_file_id = 'root'
    else:
        parent_file_id = ali_api.get_folder_by_path(pan_path, create_folder=True).file_id
    return ali_api.upload_files(file_paths=local_file_paths, parent_file_id=parent_file_id, drive_id=drive_id,
                                check_name_mode=check_name_mode)


def upload_folder(ali_api: Aligo, local_folder_path: str, pan_path: str = None, drive_id: str = None,
                  check_name_mode: CheckNameMode = "auto_rename", folder_check_name_mode: CheckNameMode = 'refuse',
                  file_filter: Callable[[os.DirEntry], bool] = lambda x: False) -> List:
    """
    上传文件夹
    :param ali_api: Aligo
    :param local_folder_path: [str] 文件夹路径
    :param pan_path: 上传到的网盘路径, 如：'我的资源/1080p'
    :param drive_id: [str] 指定网盘id, 默认为 None, 如果为 None, 则使用默认网盘
    :param check_name_mode: [CheckNameMode] 检查文件名模式, 默认为 'auto_rename'
    :param folder_check_name_mode: [CheckNameMode] 检查文件夹名模式, 默认为 'refuse'
    :param file_filter: 文件过滤函
    :return:
    """
    if pan_path is None:
        parent_file_id = 'root'
    else:
        parent_file_id = ali_api.get_folder_by_path(pan_path, create_folder=True).file_id
    return ali_api.upload_folder(local_folder_path, parent_file_id=parent_file_id, drive_id=drive_id,
                                 check_name_mode=check_name_mode, folder_check_name_mode=folder_check_name_mode,
                                 file_filter=file_filter)


def download_file_by_path(ali_api: Aligo, pan_path: str, local_path: str,
                          pan_file_filter: Callable[[BaseFile], bool] = lambda x: False) -> str:
    """
    下载文件/文件夹
    :param ali_api: Aligo
    :param pan_path: 网盘路径，如：我的资源/音乐
    :param local_path: 本地存储路径，如：D:/阿里云盘
    :param pan_file_filter: 文件过滤函数
    :return:
    """
    file = ali_api.get_file_by_path(pan_path)
    return download_file(ali_api, pan_file=file, local_path=local_path, pan_file_filter=pan_file_filter)


def download_file(ali_api: Aligo, pan_file: BaseFile, local_path: str,
                  pan_file_filter: Callable[[BaseFile], bool] = lambda x: False) -> str:
    """
    下载文件/文件夹
    :param ali_api: Aligo
    :param pan_file: 网盘文件
    :param local_path: 本地存储路径
    :param pan_file_filter: 文件过滤函数
    :return: [str] 本地文件路径
    """
    if pan_file.type == 'file':
        local_file = ali_api.download_file(file=pan_file, local_folder=local_path)
        if os.path.exists(local_file):
            if os.stat(local_file).st_size == 350:
                os.remove(local_file)
                local_file = ali_api.download_file(file_id=pan_file.file_id, local_folder=local_path)
            return local_file
    else:
        return ali_api.download_folder(folder_file_id=pan_file.file_id, local_folder=local_path,
                                       file_filter=pan_file_filter)


def walk_file_list(ali_api: Aligo, handle: Callable[[str, BaseFile], None], parent_file_id: str = 'root'):
    """
    遍历文件
    :param ali_api: Aligo
    :param handle: 文件处理函数，如：def handle(path: str, f: BaseFile):
    :param parent_file_id: 文件路径
    :return:
    """
    ali_api.walk_files(handle, parent_file_id=parent_file_id)
