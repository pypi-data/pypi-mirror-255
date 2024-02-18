"""
正则工具
"""
import re
from typing import AnyStr, Any


def high_light_word(content_text: str, keyword: str, high_light_tag: str = 'em') -> str:
    """
    单词高亮
    """
    if content_text:
        re_pattern = f'({re.escape(keyword)})'
        if re.search(re_pattern, content_text, flags=re.RegexFlag.I):
            return re.sub(re_pattern, f'<{high_light_tag}>\\1</{high_light_tag}>', content_text, flags=re.RegexFlag.I)
    return content_text


def get_match_groups(pattern:str, content:str) -> tuple[AnyStr | Any, ...]:
    """
    获取规则匹配的分组内容
    :param pattern: 正则表达式
    :param content: 内容
    :return: tuple或None 匹配的分组内容
    """
    re_match = re.compile(pattern, re.S).search(content)
    if re_match:
        return re_match.groups()


def get_match_first_group(pattern:str, content:str) -> str:
    """
    获取规则匹配的第一个分组内容
    :param pattern: 正则表达式
    :param content: 内容
    :return: 匹配的第一个分组内容
    """
    re_match_tuple = get_match_groups(pattern, content)
    if re_match_tuple:
        return re_match_tuple[0]


if __name__ == '__main__':
    pattern = r'<ToUserName><!\[CDATA\[(.*?)\]\]></ToUserName>'
    content = '<ToUserName><![CDATA[toUser]]></ToUserName>'
    print(get_match_first_group(pattern, content))
