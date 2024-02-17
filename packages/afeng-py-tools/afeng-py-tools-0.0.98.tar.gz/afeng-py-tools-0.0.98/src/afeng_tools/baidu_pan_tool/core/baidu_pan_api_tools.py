"""
- pip install pytest-playwright -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
"""

import os.path

from playwright.sync_api import Response
from afeng_tools.file_tool import file_tools, tmp_file_tools

auth_qrcode_image = os.path.join(tmp_file_tools.get_user_tmp_dir(), 'baidu_auth_qrcode.png')


def filter_login_qrcode_api(response: Response):
    if 'passport.baidu.com/v2/api/qrcode' in response.url:
        file_tools.save_file(response.body(), auth_qrcode_image, binary_flag=True)


def delete_login_qrcode_image():
    """删除扫码登录图片"""
    if os.path.exists(auth_qrcode_image):
        os.remove(auth_qrcode_image)
