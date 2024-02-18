"""
csv工具：
    - pandas： pip install pandas
"""
import pandas
from pandas import DataFrame


def read(csv_file: str, encoding: str = 'utf-8', sep: str = ',',
         n_rows: int = None, use_cols: list = None) -> DataFrame:
    """
    读取csv文件
    :param csv_file: csv文件
    :param encoding: 编码，默认是 utf-8
    :param sep: 指明分隔符，默认是逗号
    :param n_rows: 指明读取行数,如：2（读取0、1、2行）
    :param use_cols: 读取哪些列，如：[1,3] 读取第1、3列
    :return:
    """
    return pandas.read_csv(csv_file, encoding=encoding, sep=sep, nrows=n_rows, usecols=use_cols, dtype=str,
                           engine='python')


if __name__ == '__main__':
    csv = r'C:\Users\chentiefeng\Downloads\tushare_stock_basic_20230907151542.csv'
    df = read(csv)
    row_count, col_count = df.shape
    for row_i in range(row_count):
        for col_i in range(col_count):
            cell = df.iloc[row_i, col_i]
            print(cell, end=',')
        print()
