"""
Appium按、点工具类
使用示例：
touch_tool = TouchTool(driver=driver)
touch_tool.press_by_point(x=100, y=300).move_to(x=100, y=100).release()
"""
from appium.webdriver import WebElement
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.webdriver import WebDriver


class TouchTool:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.touch_action = TouchAction(self.driver)

    def tap(self, el: WebElement, count: int = 1) -> 'TouchTool':
        """轻点"""
        self.touch_action.tap(el, count=count)
        return self

    def tap_by_point(self, x: int, y: int, count: int = 1) -> 'TouchTool':
        """轻点"""
        self.touch_action.tap(x=x, y=y, count=count)
        return self

    def press(self, el: WebElement) -> 'TouchTool':
        """按压"""
        self.touch_action.press(el)
        return self

    def press_by_point(self, x: int, y: int) -> 'TouchTool':
        """按压点"""
        self.touch_action.press(x=x, y=y)
        return self

    def long_press(self, el: WebElement, duration: int = 1000) -> 'TouchTool':
        """长按"""
        self.touch_action.long_press(el, duration=duration)
        return self

    def long_press_by_point(self, x: int, y: int, duration: int = 1000) -> 'TouchTool':
        """长按点"""
        self.touch_action.long_press(x=x, y=y, duration=duration)
        return self

    def wait(self, milli_seconds: int = 1000) -> 'TouchTool':
        """等待（毫秒）"""
        self.touch_action.wait(milli_seconds)
        return self

    def move_to(self, x: int, y: int) -> 'TouchTool':
        """移动"""
        self.touch_action.move_to(x=x, y=y)
        return self

    def release(self):
        """释放按压、长按、移动后的执行操作"""
        self.touch_action.release().perform()
        return self

