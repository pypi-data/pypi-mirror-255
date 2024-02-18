from typing import Optional, Callable, Union

from playwright.sync_api import sync_playwright, ProxySettings, Browser, BrowserContext, Page

from afeng_tools.decorator_tool.decorator_tools import run_func


def auto_input(input_type: Union[Browser, BrowserContext, Page] = Page, headless: bool = True,
               timeout: float = 1000 * 60 * 10, proxy: Optional[ProxySettings] = None, is_max: bool = False,
               storage_state: str = None):
    """注解：自动化注入 web_browser:Browser | web_context:BrowserContext | web_page:Page, 默认注入Page"""
    def auto_wrapper(func: Callable):
        def func_wrapper(*args, **kwargs):
            if input_type == Browser and 'web_browser' in kwargs:
                return run_func(func, *args, **kwargs)
            if input_type == BrowserContext and 'web_context' in kwargs:
                return run_func(func, *args, **kwargs)
            if input_type == Page and 'web_page' in kwargs:
                return run_func(func, *args, **kwargs)

            with sync_playwright() as pw:
                browser_args = []
                if is_max:
                    browser_args.append('--start-maximized')
                browser = pw.chromium.launch(headless=headless, timeout=timeout, proxy=proxy,
                                             args=browser_args)
                context = None
                page = None
                try:
                    if input_type == Browser:
                        kwargs['web_browser'] = browser
                    if input_type == BrowserContext:
                        context = browser.new_context(no_viewport=True, storage_state=storage_state)
                        kwargs['web_context'] = context
                    if input_type == Page:
                        context = browser.new_context(no_viewport=True, storage_state=storage_state)
                        page = context.new_page()
                        kwargs['web_page'] = page
                    return run_func(func, *args, **kwargs)
                finally:
                    if page:
                        page.close()
                    if context:
                        context.close()
                    browser.close()
        return func_wrapper
    return auto_wrapper
