"""
系统工具
"""
import os


def get_user_home() -> str:
    """获取用户目录"""
    return os.path.expanduser('~')
