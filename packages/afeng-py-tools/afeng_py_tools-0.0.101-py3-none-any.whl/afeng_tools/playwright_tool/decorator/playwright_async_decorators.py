from typing import Callable, Optional, Union

from playwright.async_api import async_playwright, ProxySettings, Browser, BrowserContext, Page

from afeng_tools.decorator_tool.decorator_tools import run_async_func


def auto_input(input_type: Union[Browser, BrowserContext, Page] = Page, headless: bool = True,
               timeout: float = 1000 * 60 * 10, proxy: Optional[ProxySettings] = None):
    """注解：自动化注入 web_browser:Browser | web_context:BrowserContext | web_page:Page, 默认注入Page"""
    def auto_wrapper(func: Callable):
        async def func_wrapper(*args, **kwargs):
            if input_type == Browser and 'web_browser' in kwargs:
                return await run_async_func(func, *args, **kwargs)
            if input_type == BrowserContext and 'web_context' in kwargs:
                return await run_async_func(func, *args, **kwargs)
            if input_type == Page and 'web_page' in kwargs:
                return await run_async_func(func, *args, **kwargs)

            async with async_playwright() as pw:
                browser = await pw.chromium.launch(headless=headless, timeout=timeout, proxy=proxy)
                context = None
                page = None
                try:
                    if input_type == Browser:
                        kwargs['web_browser'] = browser
                    if input_type == BrowserContext:
                        context = await browser.new_context()
                        kwargs['web_context'] = context
                    if input_type == Page:
                        context = await browser.new_context()
                        page = await context.new_page()
                        kwargs['web_page'] = page
                    return await run_async_func(func, *args, **kwargs)
                finally:
                    if page:
                        await page.close()
                    if context:
                        await context.close()
                    await browser.close()
        return func_wrapper
    return auto_wrapper

