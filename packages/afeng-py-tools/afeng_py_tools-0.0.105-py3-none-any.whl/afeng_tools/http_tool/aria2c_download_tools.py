import os
import subprocess

from afeng_tools.log_tool.loguru_tools import get_logger, log_error

logger = get_logger()


def download_file(down_url:str, save_path:str, save_file_name:str=None, referer:str=''):
    try:
        subprocess.run(['aria2c', '-h'], capture_output=True)
        logger.info('发现 aria2c, 将使用 aria2c 下载文件')
        cmd = ' '.join([
            f'aria2c "{down_url}"',
            f'--referer={referer}',
            f'-d "{save_path}"',
            f'-o "{save_file_name}"'
            f'-x 16',
            f'-s 8',
        ])
        # print(cmd)
        os.system(cmd)

    except FileNotFoundError as e:
        log_error(logger, '未发现 aria2c', e)
