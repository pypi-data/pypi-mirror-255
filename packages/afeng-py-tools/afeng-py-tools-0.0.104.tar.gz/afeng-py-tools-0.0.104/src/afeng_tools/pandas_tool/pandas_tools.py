"""
pandas工具： pip install pandas
"""
from pandas import DataFrame


def get_size(df: DataFrame):
    row_count, col_count = df.shape
    return row_count, col_count


def get_columns(df: DataFrame):
    return df.columns


def get_index(df: DataFrame):
    return df.index


def get_values(df: DataFrame):
    return df.values


def get_cols_by_column(df: DataFrame, column_list: list):
    return df[column_list]


def get_cols_by_column2(df: DataFrame, column_list: list):
    return df.loc[:, column_list]


def get_cols_by_index(df: DataFrame, col_index_list: list):
    """获取第col_index_list列的值"""
    return df.iloc[:col_index_list]


def get_rows_by_index_name(df: DataFrame, index_name_list: list):
    return df.loc[index_name_list]


def get_rows_by_index(df: DataFrame, index_list: list):
    return df.iloc[index_list]
