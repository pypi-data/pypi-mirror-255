"""
jieba: pip install jieba -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
"""
import jieba


def word_cut(text_content: str, cut_all: bool = False, hmm: bool = True) -> list[str]:
    """
    精确模式分词
    @param text_content: 分词文本
    @param cut_all: 全模式分词, 从待分词内容的第一个字开始遍历，将每一个字作为词语的第一个字，返回所有可能的词语，会重复利用词语和字，因此也可能会出现多种含义。
    @param hmm: 根据HMM模型（隐马尔可夫模型）自动识别新词。
    @return: list[str]
    """
    cut_result = jieba.cut(text_content, cut_all=cut_all, HMM=hmm)
    return list(cut_result)


def word_cut_for_search(text_content: str) -> list[str]:
    """
    搜索引擎分词： 搜索引擎模式在精确模式的基础上，对精确模式中的长词，再按照全模式进一步分词，用于搜索时可以匹配到更多的结果。
    """
    cut_result = jieba.cut(text_content, cut_all=True)
    return list(cut_result)


if __name__ == '__main__':
    print(word_cut('迅雷不及掩耳盗铃儿响叮当仁不让世界充满爱之势'))
    print(word_cut_for_search('迅雷不及掩耳盗铃儿响叮当仁不让世界充满爱之势'))
