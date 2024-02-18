import os.path
import subprocess
import sys
from typing import Union, Type

from scrapy import Spider
from scrapy.cmdline import execute
from scrapy.crawler import CrawlerProcess, Crawler
from scrapy.utils.project import get_project_settings


def run_spider(spider_dir: str, spider_name: str, output_file: str = None, is_reactor: bool = True, is_wait: bool = False, **kwargs):
    sys.path.append(spider_dir)
    tmp_cwd = os.getcwd()
    os.chdir(spider_dir)
    cmd_list = ['scrapy', 'crawl', spider_name]
    if kwargs:
        for arg_name, arg_value in kwargs.items():
            cmd_list.append('-a')
            cmd_list.append(f'{arg_name}={arg_value}')
    if output_file:
        cmd_list.append('-o')
        cmd_list.append(output_file)
    if is_reactor:
        if is_wait:
            subprocess.check_output(cmd_list)
        else:
            subprocess.Popen(cmd_list, shell=True)
    else:
        execute(cmd_list)
    os.chdir(tmp_cwd)


def run_crawler(crawler_or_spider_cls: Union[Type[Spider], str, Crawler], crawler_dir: str = None, **kwargs):
    """
    运行爬虫（等待结果）
    :param crawler_or_spider_cls:爬虫类
    :param crawler_dir: 爬虫路径
    :param kwargs:参数
    :return:
    """
    sys.path.append(crawler_dir)
    tmp_cwd = os.getcwd()
    os.chdir(crawler_dir)
    settings = get_project_settings()
    crawler_process = CrawlerProcess(settings)
    crawler_process.crawl(crawler_or_spider_cls, **kwargs)
    # 启动爬虫
    crawler_process.start()
    os.chdir(tmp_cwd)


if __name__ == '__main__':
    spider_path = os.path.dirname(os.path.abspath(__file__))
    run_spider(spider_path, 'quotes')
