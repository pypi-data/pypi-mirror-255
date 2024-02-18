"""
东方财富的URL配置
"""
import math
import random

rnd = math.floor(random.random() * 99 + 1)
rnd2 = math.floor(random.random() * 99 + 1)

# 开发URL
development_urls = {
    'dataurl': '//reportapi.uat.emapd.com/',
    'quoteurl': '//push2.eastmoney.com/',
    'quotehisurl': '//push2his.eastmoney.com/',
    'dcfmurl': '//dcfm.eastmoney.com/',
    'anoticeurl': '//np-anotice-stock.eastmoney.com/',
    'cnoticeurl': '//np-cnotice-stock.eastmoney.com/',
    'datacenter': '//datacenter-web.eastmoney.com/',
    'soapi': '//searchapi.eastmoney.com/',
    'cmsdataapi': '//cmsdataapi.eastmoney.com/',
    'newsinfo': '//newsinfo.eastmoney.com/',
    # 老资讯接口
    'old_zixun_api': "//cmsdataapi.eastmoney.com/",
    # 新资讯接口
    'new_zixun_api': "//np-listapi.eastmoney.com/",
    # 公告
    'new_notice_api': "//np-anotice-stock.eastmoney.com/",
    # 行情
    'quote_api': "//push2.eastmoney.com/",
    # 行情推送接口
    'quote_push_api': "//" + str(rnd) + ".push2.eastmoney.com/",
    # 行情历史数据接口
    'quote_history_api': "//push2his.eastmoney.com/",
    # 行情历史数据推送接口
    'quote_history_push_api': "//" + str(rnd2) + ".push2his.eastmoney.com/",
    # 快讯
    'kuaixun_api': "//newsinfo.eastmoney.com/",
    # 老的数据接口
    'old_datacenter': "//dcfm.eastmoney.com/",
    # 静态行情图-分时图
    'chart_time': "//webquotepic.eastmoney.com/",
    # 静态行情图-延迟分时图
    'chart_time_delay': "//delaywebquotepic.eastmoney.com/",
    # 静态行情图-K线图
    'chart_kline': "//webquoteklinepic.eastmoney.com/",
    # 静态行情图-延迟K线图
    'chart_kline_delay': "//delaywebquoteklinepic.eastmoney.com/",
    # 研报
    'report_api': "//reportapi.eastmoney.com/",
    # 路演api
    'roadshow_api': "//list.lvb.eastmoney.com/",
    # 数据接口
    'datainterface': "//datainterface.eastmoney.com/",
    # 数据4期
    'datacenter4': "//datacenter-web.eastmoney.com/",
    # 期货接口
    'qihuo_api': "//futsseapi.eastmoney.com/",
    # 期货推送接口
    'qihuo_sse_api': "//" + str(rnd2) + ".futsseapi.eastmoney.com/",
    # 期货静态接口
    'qihuo_static': "//futsse-static.eastmoney.com/",
    # 基金接口
    'fund_api': "//fundwebapi.eastmoney.com/",
    # 盘口异动接口
    'changes_api': "//push2ex.eastmoney.com/"
}

# 测试URL
test_urls = {
    'dataurl': '//reportapi.uat.emapd.com/',
    'quoteurl': '//push2.eastmoney.com/',
    'quotehisurl': '//push2his.eastmoney.com/',
    'dcfmurl': '//dcfm.eastmoney.com/',
    'anoticeurl': '//np-anotice-stock-test.eastmoney.com/',
    'cnoticeurl': '//np-cnotice-stock-test.emapd.com/',
    'datacenter': '//testdatacenter.eastmoney.com/',
    'soapi': '//searchapi.eastmoney.com/',
    'cmsdataapi': '//cmsdataapi.eastmoney.com/',
    'newsinfo': '//newsinfo.eastmoney.com/',
    # 老资讯接口
    'old_zixun_api': "//cmsdataapi.eastmoney.com/",
    # 新资讯接口
    'new_zixun_api': "//np-listapi.eastmoney.com/",
    # 公告
    'new_notice_api': "//np-anotice-stock-test.eastmoney.com/",
    # 行情
    'quote_api': "//push2test.eastmoney.com/",
    # 行情推送接口
    'quote_push_api': "//push2test.eastmoney.com/",
    # 行情历史数据接口
    'quote_history_api': "//push2test.eastmoney.com/",
    # 行情历史数据推送接口
    'quote_history_push_api': "//push2test.eastmoney.com/",
    # 快讯
    'kuaixun_api': "//newsinfo.eastmoney.com/",
    # 老的数据接口
    'old_datacenter': "//dcfm.eastmoney.com/",
    # 静态行情图-分时图
    'chart_time': "http://61.129.249.32:8870/",
    # 静态行情图-延迟分时图
    'chart_time_delay': "http://61.129.249.32:8870/",
    # 静态行情图-K线图
    'chart_kline': "http://61.129.249.32:8871/",
    # 静态行情图-延迟K线图
    'chart_kline_delay': "http://61.129.249.32:8871/",
    # 研报
    'report_api': "//reportapi.eastmoney.com/",
    # 路演api
    'roadshow_api': "//list-qas.lvb.eastmoney.com/",
    # 数据接口
    'datainterface': "//datainterface.eastmoney.com/",
    # 数据4期
    'datacenter4': "//testdatacenter.eastmoney.com/",
    # 期货接口
    'qihuo_api': "//futssetest.eastmoney.com/",
    # 期货推送接口
    'qihuo_sse_api': "http://futssetest.eastmoney.com/",
    # 期货静态接口
    'qihuo_static': "//static.futssetest.eastmoney.com/",
    # 基金接口
    'fund_api': "//fundwebapi.eastmoney.com/",
    # 盘口异动接口
    'changes_api': "//push2ex.eastmoney.com/"
}

# 测试1URL
test1_urls = {
    # 老资讯接口
    'old_zixun_api': "//cmsdataapi.eastmoney.com/",
    # 新资讯接口
    'new_zixun_api': "//np-listapi.eastmoney.com/",
    # 公告
    'new_notice_api': "//np-anotice-stock-test.eastmoney.com/",
    # 行情
    'quote_api': "//push2test.eastmoney.com/",
    # 行情推送接口
    'quote_push_api': "//push2test.eastmoney.com/",
    # 行情历史数据接口
    'quote_history_api': "//push2test.eastmoney.com/",
    # 行情历史数据推送接口
    'quote_history_push_api': "//push2test.eastmoney.com/",
    # 快讯
    'kuaixun_api': "//newsinfo.eastmoney.com/",
    # 老的数据接口
    'old_datacenter': "//dcfm.eastmoney.com/",
    # 静态行情图-分时图
    'chart_time': "http://61.129.249.32:8870/",
    # 静态行情图-延迟分时图
    'chart_time_delay': "http://61.129.249.32:8870/",
    # 静态行情图-K线图
    'chart_kline': "http://61.129.249.32:8871/",
    # 静态行情图-延迟K线图
    'chart_kline_delay': "http://61.129.249.32:8871/",
    # 研报
    'report_api': "//reportapi.eastmoney.com/",
    # 路演api
    'roadshow_api': "//list-qas.lvb.eastmoney.com/",
    # 数据接口
    'datainterface': "//datainterface.eastmoney.com/",
    # 数据4期
    'datacenter4': "//testdatacenter.eastmoney.com/",
    # 期货接口
    'qihuo_api': "//futssetest1.eastmoney.com/",
    # 期货推送接口
    'qihuo_sse_api': "http://futssetest1.eastmoney.com/",
    # 期货静态接口
    'qihuo_static': "//static.futssetest.eastmoney.com/",
    # 基金接口
    'fund_api': "//fundwebapi.eastmoney.com/",
    # 盘口异动接口
    'changes_api': "//push2ex.eastmoney.com/"
}

# 灰度测试URL
gray_urls = {
    'dataurl': '//reportapi.eastmoney.com/',
    'quoteurl': '//push2.eastmoney.com/',
    'quotehisurl': '//push2his.eastmoney.com/',
    'dcfmurl': '//dcfm.eastmoney.com/',
    'anoticeurl': '//np-anotice-stock.eastmoney.com/',
    'cnoticeurl': '//np-cnotice-stock.eastmoney.com/',
    'datacenter': '//graydatacenter.eastmoney.com/',
    'soapi': '//searchapi.eastmoney.com/',
    'cmsdataapi': '//cmsdataapi.eastmoney.com/',
    'newsinfo': '//newsinfo.eastmoney.com/'
}

# 生产URL
production_urls = {
    'dataurl': '//reportapi.eastmoney.com/',
    'quoteurl': '//push2.eastmoney.com/',
    'quotehisurl': '//push2his.eastmoney.com/',
    'dcfmurl': '//dcfm.eastmoney.com/',
    'anoticeurl': '//np-anotice-stock.eastmoney.com/',
    'cnoticeurl': '//np-cnotice-stock.eastmoney.com/',
    'datacenter': '//datacenter-web.eastmoney.com/',
    'soapi': '//searchapi.eastmoney.com/',
    'cmsdataapi': '//cmsdataapi.eastmoney.com/',
    'newsinfo': '//newsinfo.eastmoney.com/',
    # 老资讯接口
    'old_zixun_api': "//cmsdataapi.eastmoney.com/",
    # 新资讯接口
    'new_zixun_api': "//np-listapi.eastmoney.com/",
    # 公告
    'new_notice_api': "//np-anotice-stock.eastmoney.com/",
    # 行情
    'quote_api': "//push2.eastmoney.com/",
    # 行情推送接口
    'quote_push_api': "//" + str(rnd) + ".push2.eastmoney.com/",
    # 行情历史数据接口
    'quote_history_api': "//push2his.eastmoney.com/",
    # 行情历史数据推送接口
    'quote_history_push_api': "//" + str(rnd2) + ".push2his.eastmoney.com/",
    # 快讯
    'kuaixun_api': "//newsinfo.eastmoney.com/",
    # 老的数据接口
    'old_datacenter': "//dcfm.eastmoney.com/",
    # 静态行情图-分时图
    'chart_time': "//webquotepic.eastmoney.com/",
    # 静态行情图-延迟分时图
    'chart_time_delay': "//delaywebquotepic.eastmoney.com/",
    # 静态行情图-K线图
    'chart_kline': "//webquoteklinepic.eastmoney.com/",
    # 静态行情图-延迟K线图
    'chart_kline_delay': "//delaywebquoteklinepic.eastmoney.com/",
    # 研报
    'report_api': "//reportapi.eastmoney.com/",
    # 路演api
    'roadshow_api': "//list.lvb.eastmoney.com/",
    # 数据接口
    'datainterface': "//datainterface.eastmoney.com/",
    # 数据4期
    'datacenter4': "//datacenter-web.eastmoney.com/",
    # 期货接口
    'qihuo_api': "//futsseapi.eastmoney.com/",
    # 期货推送接口
    'qihuo_sse_api': "//" + str(rnd2) + ".futsseapi.eastmoney.com/",
    # 期货静态接口
    'qihuo_static': "//futsse-static.eastmoney.com/",
    # 基金接口
    'fund_api': "//fundwebapi.eastmoney.com/",
    # 盘口异动接口
    'changes_api': "//push2ex.eastmoney.com/"
}


def get_url(url_key):
    # 生产环境
    env = 'dev'
    if env == 'dev':
        return development_urls[url_key]
    elif env == 'test':
        return test_urls[url_key]
    elif env == 'test1':
        return test1_urls[url_key]
    elif env == 'gray':
        return gray_urls[url_key]
    return production_urls[url_key]
