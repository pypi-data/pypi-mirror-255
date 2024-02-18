"""
文章拆分工具
"""


def split_to_sentence(paragraph_text: str) -> list[str]:
    """
    段落拆分为句子（以"。"为分割句子）
    :param paragraph_text: 段落文本
    :return: 句子列表
    """
    sentence_list = []
    for tmp_sentence in paragraph_text.split('。'):
        if tmp_sentence.strip():
            sentence_list.append(tmp_sentence.strip())
    return sentence_list


def split_to_paragraph(article_text: str) -> list[str]:
    """
    把文章拆分为段落(以 换行符"\n"分割为段落)
    :param article_text: 文章文本
    :return: 段落列表
    """
    paragraph_list = []
    for tmp_paragraph in article_text.split('\n'):
        if tmp_paragraph.strip():
            paragraph_list.append(tmp_paragraph.strip())
    return paragraph_list


def replace_special_char(article_text: str) -> str:
    """
    替换特殊字符
    :param article_text:
    :return: 替换后的文本
    """
    text = article_text.replace('-', '')
    text = text.replace(' ', '')
    text = text.replace('’', '')
    text = text.replace('﨑', '崎')
    text = text.replace("[", ' ')
    text = text.replace("]", ' ')
    text = text.replace('　', ' ')
    text = text.replace("，]", "")
    text = text.replace("１", "1")
    text = text.replace("２", '2')
    text = text.replace("６", "6")
    text = text.replace("〔", "")
    text = text.replace("─", "")
    text = text.replace("┬", "")
    text = text.replace("┼", "")
    text = text.replace("┴", "")
    text = text.replace("〖", " ")
    text = text.replace("〗", " ")
    text = text.replace("礻殳", "祋")
    return text


def split_article(article_text: str) -> list[list[str]]:
    """
    拆分文章为句子
    :param article_text: 文章文本
    :return: list[list[句子]]
    """
    paragraph_list = split_to_paragraph(replace_special_char(article_text))
    result_list = []
    for tmp_paragraph in paragraph_list:
        result_list.append(split_to_sentence(tmp_paragraph))
    return result_list
