"""
http的mimetypes工具
"""
import mimetypes


def get_mimetype(file_name):
    """
    通过名称获取 mimetype
    :param file_name: 文件名
    :return: 与文件名匹配的 mimetype
    """
    return mimetypes.guess_type(file_name)
