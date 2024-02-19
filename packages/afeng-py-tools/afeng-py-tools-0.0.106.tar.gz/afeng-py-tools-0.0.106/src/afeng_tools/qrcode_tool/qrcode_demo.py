from afeng_tools.qrcode_tool.qrcode_tools import make_qrcode_image


def print_qrcode_info(data_str: str):
    """测试打印二维码"""
    img = make_qrcode_image(data_str, 'output/test,png')
    img.show()
    print('box_size:', img.box_size, '\n',
          'border:', img.border, '\n',
          '前景色：', img.fill_color, '\n'
                                     '图片像素大小：', img.pixel_size, '\n',
          '图片类型:', img.kind, '\n',  # 效果等同于img.check_kind(kind=None)
          'version:', int(1 + (img.width - 21) / 4)  # img.width的值就是每行或每列的box的数量
          )


if __name__ == '__main__':
    print_qrcode_info('测试')