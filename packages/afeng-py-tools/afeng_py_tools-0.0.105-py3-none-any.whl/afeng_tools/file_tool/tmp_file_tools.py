"""
临时文件工具
"""
import tempfile

from afeng_tools.decorator_tool import decorator_tools


def auto_tmp_file(func):
    """自动注入临时文件：tmp_file. 当执行结束，文件会自动删除"""

    def wrap(*args, **kwargs):
        if 'tmp_file' in kwargs:
            return decorator_tools.run_func(func, *args, **kwargs)
        with tempfile.TemporaryFile() as fd:
            kwargs['tmp_file'] = fd
            return decorator_tools.run_func(func, *args, **kwargs)


def auto_tmp_dir(func):
    """自动注入临时目录：tmp_dir. 当执行结束，目录会自动删除"""

    def wrap(*args, **kwargs):
        if 'tmp_dir' in kwargs:
            return decorator_tools.run_func(func, *args, **kwargs)
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            kwargs['tmp_dir'] = tmp_dir_name
            return decorator_tools.run_func(func, *args, **kwargs)


def write_line(tmp_file, line_list: list[str]):
    """写入行"""
    for tmp_line in line_list:
        tmp_file.write(f'{tmp_line}\n'.encode('utf-8'))


def read_line(tmp_file) -> list[str]:
    """读取行"""
    # 将文件指针移到开始处，准备读取文件
    tmp_file.seek(0)
    return [tmp_line.decode('utf-8') for tmp_line in tmp_file.readlines()]


def get_user_tmp_dir() -> str:
    """获取用户的临时目录"""
    return tempfile.gettempdir()

if __name__ == '__main__':
    print(get_user_tmp_dir())