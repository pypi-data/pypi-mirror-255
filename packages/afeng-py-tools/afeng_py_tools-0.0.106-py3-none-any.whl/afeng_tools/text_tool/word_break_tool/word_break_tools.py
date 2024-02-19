"""
分词工具
"""
from afeng_tools.text_tool.word_break_tool import jieba_tools


def word_cut(text_content: str) -> list[str]:
    return jieba_tools.word_cut(text_content)


def word_cut_for_search(text_content: str) -> list[str]:
    return jieba_tools.word_cut_for_search(text_content)
