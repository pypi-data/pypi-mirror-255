"""
数字转汉子工具：
1、可以使用模块：pip install cn2an
    将字符串中的数字转为汉字： cn2an.transform(str_data, "an2cn")

"""
import re


def num_to_chinese(num_value: int | float, mode: str = 'low'):
    """
    数字转汉字
    :param num_value:
    :param mode: 模式
         low 模式（默认）下，数字转化为小写的中文数字，如：123  一百二十三    -123  负一百二十三   1.23  一点二三
         up 模式下，数字转化为大写的中文数字， 如：123   壹佰贰拾叁
         rmb 模式下，数字转化为人民币专用的描述， 如：123  壹佰贰拾叁元整
    :return:
    """
    import cn2an
    return cn2an.an2cn(str(num_value), mode)


low_mode_num_info = {
    'chinese_num_list': ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九'],
    'chinese_num_low_dict': {0: '零', 1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '七', 8: '八', 9: '九'},
    'chinese_num_high_dict': {10: '十', 100: '百', 1000: '千', 10000: '万', 100000000: '亿'},
    'chinese_num_dict': {0: '零', 1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '七', 8: '八', 9: '九', 10: '十', 100: '百', 1000: '千', 10000: '万', 100000000: '亿'}
}
up_mode_num_info = {
    'chinese_num_list': ["零", "壹", "贰", "叁", "肆", "伍", "陆", "柒", "捌", "玖"],
    'chinese_num_low_dict': {0: '零', 1: '壹', 2: '贰', 3: '叁', 4: '肆', 5: '伍', 6: '陆', 7: '柒', 8: '捌', 9: '玖'},
    'chinese_num_high_dict': {10: '拾', 100: '佰', 1000: '仟', 10000: '万', 100000000: '亿'},
    'chinese_num_dict': {0: '零', 1: '壹', 2: '贰', 3: '叁', 4: '肆', 5: '伍', 6: '陆', 7: '柒', 8: '捌', 9: '玖', 10: '拾', 100: '佰', 1000: '仟', 10000: '万', 100000000: '亿'}
}


def to_chinese(num_value: int, mode: str = 'low'):
    """
    数字转汉子
    :param num_value:
    :param mode: 模式
         low 模式（默认）下，数字转化为小写的中文数字，如：123  一百二十三    -123  负一百二十三   1.23  一点二三
         up 模式下，数字转化为大写的中文数字， 如：123   壹佰贰拾叁
    :return:
    """
    mode_num_info = low_mode_num_info
    if mode == 'up':
        mode_num_info = up_mode_num_info
    if num_value < 0:
        return '负' + to_chinese(abs(num_value), mode)
    elif num_value < 10:
        return mode_num_info['chinese_num_list'][num_value]
    elif num_value < 100:
        if num_value % 10 == 0:
            return mode_num_info['chinese_num_list'][num_value // 10] + mode_num_info['chinese_num_high_dict'].get(10)
        else:
            return mode_num_info['chinese_num_list'][num_value // 10] + mode_num_info['chinese_num_high_dict'].get(10) + \
                mode_num_info['chinese_num_list'][num_value % 10]
    else:
        for key in sorted(mode_num_info['chinese_num_high_dict'].keys(), reverse=True):
            if num_value // key > 0:
                return to_chinese(num_value // key, mode) + mode_num_info['chinese_num_high_dict'][key] + to_chinese(
                    num_value % key, mode)


if __name__ == '__main__':
    print(to_chinese(1101111111, mode='up'))
