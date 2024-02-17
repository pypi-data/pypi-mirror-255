from playwright.sync_api import Page

from afeng_tools.playwright_tool.decorator.playwright_decorators import auto_input


@auto_input(headless=False)
def run_test(web_page: Page = None):
    web_page.goto('https://data.eastmoney.com/stockcomment/stock_code/688981.html')
    print(web_page.title())
    # 笔画详情
    for i, tmp_stroke_unit in enumerate(web_page.locator('.word-stroke-detail').all()):
        tmp_stroke_unit.locator('g').screenshot(path=f'output/{i + 1}.png')


@auto_input(headless=False)
def run_test(stock_code, web_page: Page = None):
    web_page.goto('https://data.eastmoney.com/stockcomment/stock_code/688981.html')
    print(web_page.title())
    # 笔画详情
    for i, tmp_stroke_unit in enumerate(web_page.locator('.word-stroke-detail').all()):
        tmp_stroke_unit.locator('g').screenshot(path=f'output/{i + 1}.png')


if __name__ == '__main__':
    run_test()
