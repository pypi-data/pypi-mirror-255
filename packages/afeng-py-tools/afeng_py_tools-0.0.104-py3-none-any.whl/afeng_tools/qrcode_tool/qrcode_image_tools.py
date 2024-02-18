"""
二维码图片工具类
- pillow: pip install pillow  -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
"""
import os.path
import platform
from pathlib import Path

from PIL import Image


def get_blocks():
    """获取二维码用到的方块"""
    if platform.system() == "Windows":
        white_block = '▇'
        black_block = '  '
        new_line = '\n'
    else:
        white_block = '\033[0;37;47m  '
        black_block = '\033[0;37;40m  '
        new_line = '\033[0m\n'
    return white_block, black_block, new_line


def get_box_size(img: Image):
    """获取每一个二维码的每个box像素块的大小（像素）"""
    width, height = img.size
    x1, y1, x2, y2 = 0, 0, 0, 0
    have_black = False
    hava_white = False
    for y in range(height):
        for x in range(width):
            tmp_pix = img.getpixel((x, y))
            if tmp_pix[:3] == (0, 0, 0) and not have_black:
                x1, y1 = x, y
                have_black = True
            if have_black and tmp_pix[:3] == (255, 255, 255):
                x2, y2 = x, y
                hava_white = True
                break
        if hava_white:
            break
    for x in range(x1, x2):
        for y in range(x1, x2):
            tmp_pix = img.getpixel((y, x))
            if tmp_pix[:3] == (255, 255, 255):
                #  每个黑色格子的像素点大小
                cell_width = y - y1
                cell_height = x - x1
                return cell_width, cell_height


def print_qrcode_image(qrcode_image_file):
    """打印二维码图片到控制台"""
    img = Image.open(qrcode_image_file).convert("RGB")
    box_width, box_height = get_box_size(img)
    width, height = img.size
    white_block, black_block, new_line = get_blocks()
    output = ''
    for y in range(0, height, box_height):
        for x in range(0, width, box_width):
            tmp_pix = img.getpixel((x, y))
            if tmp_pix[:3] == (0, 0, 0):
                # 黑色像素
                output += white_block
            elif tmp_pix[:3] == (255, 255, 255):
                # 白色像
                output += black_block
        output += new_line
    print(output)
    return output


def print_qrcode(qrcode_image_file: str):
    im = Image.open(qrcode_image_file)
    width, height = 33, 33
    im = im.resize((width, height), Image.NEAREST)
    text = ''
    for w in range(width):
        for h in range(height):
            res = im.getpixel((h, w))
            text += '  ' if res == 0 else '██'
        text += '\n'
    print(text)
    return text


if __name__ == '__main__':
    qrcode_image = os.path.join(Path(__file__).parent, '../../../tool/image/data/qr_test.png')
    # print_qrcode_image(qrcode_image)
    print_qrcode(qrcode_image)