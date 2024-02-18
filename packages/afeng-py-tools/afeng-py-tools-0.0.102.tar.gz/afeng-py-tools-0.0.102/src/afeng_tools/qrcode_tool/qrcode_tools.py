"""
二维码工具: pip install qrcode -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
"""
import base64
import io

import qrcode
import qrcode.image.svg
from qrcode.compat.pil import Image


def get_qrcode_svg_factory(method: str = None):
    """获取svg的factory"""
    if method == 'basic':
        # Simple factory, just a set of rects.
        factory = qrcode.image.svg.SvgImage
    elif method == 'fragment':
        # Fragment factory (also just a set of rects)
        factory = qrcode.image.svg.SvgFragmentImage
    else:
        # Combined path factory, fixes white space that may occur when zooming
        factory = qrcode.image.svg.SvgPathImage
    return factory


def make_qrcode_svg(data_str: str, save_svg: str, method: str = None) -> Image:
    """创建二维码svg"""
    pil_img = qrcode.make(data_str, image_factory=get_qrcode_svg_factory(method=method))
    pil_img.save(save_svg)
    return pil_img


def make_qrcode(data_str: str, save_image: str, option: dict = None) -> Image:
    """
    创建二维码
    :param data_str: 数据文件
    :param save_image: 保存的二维码图片
    :param option: 二维码配置
    :return: pil图片
    """
    default_option = {
        # 二维码的每个box像素块的大小是多少像素
        'box_size': 10,
        # 二维码与图片的边缘的距离是多少个box
        'border': 2,
        # 前景色
        'fill_color': 'black',
        # 背景色
        'back_color': 'white',
        # 图片像素大小
        'pixel_size': 290,
        # 图片类型
        'kind': 'PNG',
    }
    if not option:
        option = default_option
    qr = qrcode.QRCode(
        # version值范围[1-40]整数，1表示21x21矩阵，值为None，qr.make(fit=True),则系统自动调整大小
        version=4,  # 直观的感受是二维码中像素的密集程度，数越大，密集程度越高
        error_correction=qrcode.constants.ERROR_CORRECT_M,  # 容错率 7%，15%，25%，30%
        **option
    )
    # 二维码内容
    qr.add_data(data_str)
    # 图片中的二维码大小自适应，以保证二维码内容能完整绘制
    qr.make(fit=True)
    # 前景、背景色
    pil_img = qr.make_image(fill_color="blue", back_color="white")
    pil_img.save(save_image)
    return pil_img


def make_qrcode_image(data_str: str, save_image: str) -> Image:
    """创建二维码图片"""
    pil_img = qrcode.make(data_str)
    pil_img.save(save_image)
    return pil_img


def make_qrcode_image_base64(data_str: str, border: int = 2) -> str:
    """创建二维码图片"""
    pil_img = qrcode.make(data_str, border=border)
    # 创建一个BytesIO对象，用于临时存储图像数据
    image_data = io.BytesIO()
    # 将图像保存到BytesIO对象中，格式为JPEG
    pil_img.save(image_data)
    # 将BytesIO对象的内容转换为字节串
    image_data_bytes = image_data.getvalue()
    # 将图像数据编码为Base64字符串
    return 'data:image/png;base64,' + base64.b64encode(image_data_bytes).decode('utf-8')


if __name__ == '__main__':
    print(make_qrcode_image_base64('https://127.0.0.1:8080/reader/12345', border=1))
