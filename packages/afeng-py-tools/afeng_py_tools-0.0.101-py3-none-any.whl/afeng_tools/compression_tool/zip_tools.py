import os.path
import zipfile

import pyzipper

from afeng_tools.file_tool.file_tools import list_files


def run_pwd_zip(zip_file: str, file_list: list[tuple[str, str]], password: str = None):
    """
    zip加密压缩：将指定的多个文件压缩到一个 zip 文件
    :param zip_file: zip文件
    :param file_list: 待压缩的文件列表'
    :param password: 加密密码
    :return: 压缩后的zip文件
    """
    with pyzipper.AESZipFile(zip_file, "w", compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as z:
        # 设置压缩文件的密码
        if password:
            z.setpassword(password.encode('utf-8'))
        for arc_name, tmp_file in file_list:
            if os.path.isfile(tmp_file):
                z.write(tmp_file, arcname=arc_name)


def run_pwd_unzip(zip_file: str, unzip_path: str, password: str = None) -> list[str]:
    """
    解压zip
    :param zip_file: zip文件
    :param unzip_path: 解压到的地址
    :param password: 加密密码
    :return: 压缩文件列表
    """
    with pyzipper.AESZipFile(zip_file, "r") as z:
        if password:
            z.extractall(unzip_path, pwd=password.encode('utf-8'))
        else:
            # 设置解压的地址
            z.extractall(unzip_path)
        return z.namelist()


def run_zip(zip_file: str, file_list: list[tuple[str, str]], password: str = None):
    """
    zip压缩：将指定的多个文件压缩到一个 zip 文件
    :param zip_file: zip文件
    :param file_list: 待压缩的文件列表'
    :param password: 加密密码
    :return: 压缩后的zip文件
    """
    if password:
        run_pwd_zip(zip_file, file_list=file_list, password=password)
    else:
        with zipfile.ZipFile(zip_file, "w") as z:
            for arc_name, tmp_file in file_list:
                if os.path.isfile(tmp_file):
                    z.write(tmp_file, arcname=arc_name)


def run_zip_dir(zip_file: str, dir_path: str, password: str = None):
    """
    zip压缩：将指定的多个文件压缩到一个 zip 文件
    :param zip_file: zip文件
    :param dir_path: 待压缩的文件列表
    :param password: 加密密码
    :return: 压缩后的zip文件
    """
    relative_list, absolute_list = list_files(dir_path)
    run_zip(zip_file, [(tmp, absolute_list[i]) for i, tmp in enumerate(relative_list)], password=password)


def run_unzip(zip_file: str, unzip_path: str, password: str = None) -> list[str]:
    """
    解压zip
    :param zip_file: zip文件
    :param unzip_path: 解压到的地址
    :param password: 加密密码
    :return: 压缩文件列表
    """
    if password:
        run_pwd_unzip(zip_file, unzip_path=unzip_path, password=password)
    else:
        with zipfile.ZipFile(zip_file, "r") as z:
            z.extractall(unzip_path)
            return z.namelist()


if __name__ == '__main__':
    book_path = r'C:\迅雷云盘'
    run_zip_dir(r'C:\迅雷云盘\test.zip', f'C:\迅雷云盘', password='123456')
    run_unzip(r'C:\迅雷云盘\test.zip', r'C:\迅雷云盘\test01', password='123456')
