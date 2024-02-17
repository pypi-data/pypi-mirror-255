"""
文件工具
"""
import glob
import os
import re
import shutil
from typing import Union

from afeng_tools.encryption_tool import hashlib_tools
from afeng_tools.linux_tool import linux_match_tools
from afeng_tools.math_tool import random_tools


def list_path(dir_path, include_file_list=None, exclude_dir_list: list = None,
              exclude_file_list: list = None):
    """
    列出目录下的指定文件和目录
    :param dir_path: 目录路径
    :param include_file_list: 文章后缀名集合（可以用正则表达式）
    :param exclude_dir_list: 排除的子目录
    :param exclude_file_list: 排除的文件，可以用正则表达式
    :return: {‘文件名’:'文件完整路径'}
    """
    if include_file_list is None:
        include_file_list = ['*.*']
    exclude_dir_list = [] if exclude_dir_list is None else exclude_dir_list
    exclude_file_list = [] if exclude_file_list is None else exclude_file_list
    file_dict = dict()
    for tmp_file in os.listdir(dir_path):
        tmp_file_full_path = os.path.join(dir_path, tmp_file)
        if os.path.isfile(tmp_file_full_path) \
                and linux_match_tools.match_any(tmp_file, include_file_list) \
                and not linux_match_tools.match_any(tmp_file, exclude_file_list):
            tmp_file_name = tmp_file.rsplit('.', 1)[0]
            file_dict[tmp_file_name] = tmp_file_full_path
        if os.path.isdir(tmp_file_full_path) \
                and not linux_match_tools.match_any(tmp_file, exclude_dir_list):
            file_dict[tmp_file] = tmp_file_full_path
    return file_dict


def get_file_list(dir_path, filter_pattern='*.*', recursive=False):
    """
    列出文件列表
    :param dir_path: 文件路径
    :param filter_pattern: 文件名过滤模式，如：*.png
    :param recursive: 如果为True，会遍历子文件夹
    :return:
    """
    return glob.glob(os.path.join(dir_path, filter_pattern), recursive=recursive)


def get_image_list(dir_path):
    """
    获取文件夹中所有图像文件的列表
    :param dir_path: 文件路径
    :return:
    """
    return get_file_list(dir_path, '*.png')


def _sort_key_lambda(x: str) -> str:
    """
    排序键的lambda表达式
    :param x: 键x
    :return: 改动后的比较键x
    """
    if '\\' in x:
        x = x.rsplit('\\', 1)[1]
    if '/' in x:
        x = x.rsplit('/', 1)[1]
    re_search = re.search('(\d*)', x)
    if re_search:
        return str(-10000000000000 - int(re_search.group(1)))
    return str.lower(x)


def filename_sort(filename_list: list, reverse=False):
    """
    文件名排序排序
    :param filename_list: 文件名列表
    :param reverse: 是否反转
    :return: 排序后的列表（直接在原列表排序的）
    """

    filename_list.sort(
        key=lambda x: _sort_key_lambda(x),
        reverse=reverse)
    return filename_list


def random_file_name():
    """返回由时间戳+5位随机数的文件名"""
    return random_tools.random_str()


def read_file(data_file, binary_flag=False) -> Union[str, bytes]:
    """
    读取文件字符串
    :param data_file: 数据文件
    :param binary_flag: 是否是二进制文件，如果True,则按照二进制读取
    :return: None或文件内容
    """
    if os.path.isfile(data_file):
        mode = 'rb' if binary_flag else 'r'
        encoding = None if binary_flag else 'utf-8'
        with open(data_file, mode, encoding=encoding) as f:
            return f.read()


def iterate_read_file(data_file: str, binary_flag=False, buffer_size=50 * 1024):
    """
    递归读取文件字符串
    :param data_file: 数据文件
    :param binary_flag: 是否是二进制文件，如果True,则按照二进制读取
    :param buffer_size: 缓存区大小
    :return: None或文件内容
    """
    if os.path.isfile(data_file):
        mode = 'rb' if binary_flag else 'r'
        encoding = None if binary_flag else 'utf-8'
        with open(data_file, mode, encoding=encoding) as f:
            # 读取buffer_size字节的数据
            data = f.read(buffer_size)
            while data:
                # 处理数据
                yield data
                # 继续读取下一个buffer_size字节的数据
                data = f.read(buffer_size)


def save_file(file_data: str | bytes, save_file_name: str, binary_flag=False) -> str:
    """
    保存文件
    :param file_data: 文件内容
    :param save_file_name: 保存的文件
    :param binary_flag: 是否是二进制文件，如果True,则按照二进制读取
    :return: 保存的文件
    """
    mode = 'wb' if binary_flag else 'w'
    encoding = None if binary_flag else 'utf-8'
    with open(save_file_name, mode, encoding=encoding) as f:
        f.write(file_data)
    return save_file_name


def save_html_file(save_html_name: str, file_data: str | bytes, append_jinja2_raw=False):
    """
    保存html文件
    :param save_html_name: 保存的html文件
    :param file_data: 文件内容
    :param append_jinja2_raw: 添加jinja2的{% raw %}， 用于确保模板中的某些内容不会被错误地转义
    :return: 保存的html文件
    """
    binary_flag = isinstance(file_data, bytes)
    mode = 'wb' if binary_flag else 'w'
    encoding = None if binary_flag else 'utf-8'
    if append_jinja2_raw:
        if binary_flag:
            file_data = '{% raw %}'.encode('utf-8') + file_data + '{% endraw %}'.encode('utf-8')
        else:
            file_data = '{% raw %}' + file_data + '{% endraw %}'
    with open(save_html_name, mode, encoding=encoding) as f:
        f.write(file_data)
    return save_html_file


def append_file(file_data: str | bytes, save_file_name: str, binary_flag=False) -> str:
    """
    保存文件
    :param file_data: 文件内容
    :param save_file_name: 保存的文件
    :param binary_flag: 是否是二进制文件，如果True,则按照二进制读取
    :return: 保存的文件
    """
    mode = 'ab' if binary_flag else 'a'
    encoding = None if binary_flag else 'utf-8'
    with open(save_file_name, mode, encoding=encoding) as f:
        f.write(file_data)
    return save_file_name


def read_files(file_path: str, file_pattern: str) -> dict[str, str]:
    """
    读取某些文件的内容
    :param file_path: 文件路径
    :param file_pattern: 文件名规则， 如: *。css
    :return: {'文件名','文件内容'}
    """
    tmp_file_list = get_file_list(file_path, file_pattern)
    tmp_file_list = filename_sort(tmp_file_list)
    file_info_dict = {}
    for tmp_file in tmp_file_list:
        file_info_dict[os.path.split(tmp_file)[1]] = read_file(tmp_file)
    return file_info_dict


def read_files_to_one(file_path: str, file_pattern: str, join_char: str = '\n') -> str:
    """
    读取某些文件为一个字符串
    :param file_path: 文件路径
    :param file_pattern: 文件名规则， 如: *。css
    :param join_char: 文件内容拼接的字符
    :return: 文件内容拼接的字符串
    """
    file_info_dict = read_files(file_path=file_path, file_pattern=file_pattern)
    tmp_content_list = []
    for _, tmp_content in file_info_dict.items():
        tmp_content_list.append(tmp_content)
    return join_char.join(tmp_content_list)


def read_file_lines(data_file) -> list[str]:
    """
    读取文件行（空白行已经清除）
    :param data_file: 数据文件
    :return: 行数据组成的列表
    """
    with open(data_file, encoding='utf-8') as file:
        line_list = []
        for tmp_line in file.readlines():
            tmp_line = tmp_line.strip()
            if tmp_line:
                line_list.append(tmp_line)
        return line_list


def calc_new_file_name(old_file: str):
    """计算新的文件名"""
    old_file_name = old_file.split('/')[-1]
    subfix = old_file_name.rsplit('.', maxsplit=1)[-1]
    return hashlib_tools.calc_md5(old_file_name) + '.' + subfix


def list_files(dir_path: str, recursion: bool = True, include_folder: bool = True) -> tuple[list[str], list[str]]:
    """
    列出目录下所有文件
    :param dir_path: 目录
    :param recursion: 是否递归遍历子目录，默认是
    :param include_folder: 是否包含目录，默认是
    :return: (相对所有子文件、子文件夹列表，绝对所有子文件、子文件夹列表)
    """
    # 相对文件列表
    relative_file_list = []
    for tmp_dir in os.listdir(dir_path):
        abs_dir = os.path.join(dir_path, tmp_dir)
        if os.path.isdir(abs_dir):
            if include_folder:
                relative_file_list.append(tmp_dir)
            if recursion:
                tmp_relative, tmp_absolute = list_files(abs_dir, recursion=recursion, include_folder=include_folder)
                relative_file_list.extend([os.path.join(tmp_dir, temp) for temp in tmp_relative])
        else:
            relative_file_list.append(tmp_dir)
    # 绝对文件列表
    absolute_file_list = [os.path.join(dir_path, tmp_dir) for tmp_dir in relative_file_list]
    return relative_file_list, absolute_file_list


def read_file_body(data_file, start: int, length: int) -> bytes:
    """
    读取文件内容
    :param data_file: 数据内容
    :param start: 开始位置
    :param length: 读取长度
    :return: 读取到的字节码
    """
    with open(data_file, 'rb') as tmp_file:
        tmp_file.seek(start)
        return tmp_file.read(length)


one_kb = 1024
one_mb = 1024 * 1024
one_gb = 1024 * 1024 * 1024


def calc_file_size(file_size: int) -> str | None:
    """计算文件大小"""
    if file_size is None:
        return file_size
    if file_size < 1024:
        return f'{file_size}B'
    elif file_size // one_kb < 1024:
        return f'{round(file_size / one_kb, 2)}KB'
    elif file_size // one_mb < 1024:
        return f'{round(file_size / one_mb, 2)}MB'
    else:
        return f'{round(file_size / one_gb, 2)}GB'


def parse_file_size(file_size: str) -> int | None:
    """
    转换文件大小
    :param file_size: 文件大小，如：2MB
    :return: 文件大小int值
    """
    if file_size is None:
        return file_size
    file_size = file_size.strip()
    if file_size.endswith('KB'):
        return int(float(file_size.removesuffix('KB')) * one_kb)
    elif file_size.endswith('K'):
        return int(float(file_size.removesuffix('K')) * one_kb)
    elif file_size.endswith('MB'):
        return int(float(file_size.removesuffix('MB')) * one_mb)
    elif file_size.endswith('M'):
        return int(float(file_size.removesuffix('M')) * one_mb)
    elif file_size.endswith('GB'):
        return int(float(file_size.removesuffix('GB')) * one_gb)
    elif file_size.endswith('G'):
        return int(float(file_size.removesuffix('G')) * one_gb)
    elif file_size.endswith('B'):
        return int(file_size.removesuffix('B'))
    return int(file_size)


def copy_directory(source: str, destination: str, delete_old: bool = True, include_dir_name: bool = False):
    """
    复制文件夹
    :param source: 源目录
    :param destination: 目标目录
    :param delete_old: 是否删除旧的目标目录
    :param include_dir_name: 目标目录中是否包含复制后的目录名
    :return:
    """
    if not include_dir_name:
        destination = os.path.join(destination, os.path.split(source)[1])
    if delete_old and os.path.exists(destination):
        # 如果目标文件夹已存在，删除它
        shutil.rmtree(destination)
    # 复制源文件夹到目标文件夹
    shutil.copytree(source, destination)


if __name__ == '__main__':
    # test_path = 'C:\\Users\\chentiefeng\\AppData\\Local\\JianyingPro\\User Data'
    # file_list = get_file_list(test_path, '*.mp3', True)
    # for tmp in file_list:
    #     print(tmp)

    book_path = r'C:\迅雷云盘'
    relative_list, absolute_list = list_files(book_path)
    for tmp in relative_list:
        print(tmp)
    for tmp in absolute_list:
        print(tmp)
