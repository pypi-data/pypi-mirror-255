import math
import time
from typing import List

from appium import webdriver
from appium.webdriver import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from afeng_tools.appium_tool import mobile_adb_tools
from afeng_tools.appium_tool.appium_options_tools import huawei_options


class AppiumClientTool:
    def __init__(self, app_package: str, app_activity: str, appium_server_url: str = 'http://127.0.0.1:4723/wd/hub'):
        self.driver = webdriver.Remote(appium_server_url,
                                       options=huawei_options(app_package=app_package, app_activity=app_activity))

    def run_swipe(self, start_x, start_y, end_x, end_y) -> 'AppiumClientTool':
        """
        滑动屏幕
        :param start_x:
        :param start_y:
        :param end_x:
        :param end_y:
        :return: 当前类，用于链式操作
        """
        mobile_adb_tools.swipe(start_x=start_x, start_y=start_y, end_x=end_x, end_y=end_y)
        return self

    def get_viewport_rect(self):
        """
        获取当前页面的rect
        :return: 如：{'left': 0, 'top': 102, 'width': 1080, 'height': 2106}
        """
        return self.driver.capabilities['viewportRect']

    def get_viewport_size(self):
        viewport_rect = self.get_viewport_rect()
        return viewport_rect['width'], viewport_rect['height']

    def run_swipe_up(self, up_value: int = 300) -> 'AppiumClientTool':
        viewport_rect = self.get_viewport_rect()
        left, top = viewport_rect['left'], viewport_rect['top']
        width, height = viewport_rect['width'], viewport_rect['height']
        x = left + math.floor(width / 2)
        y = top + math.floor(height / 2)
        mobile_adb_tools.swipe(start_x=x, start_y=y, end_x=x, end_y=y - up_value if y - up_value > top else top)
        return self

    def run_swipe_down(self, down_value: int = 300) -> 'AppiumClientTool':
        viewport_rect = self.get_viewport_rect()
        left, top = viewport_rect['left'], viewport_rect['top']
        width, height = viewport_rect['width'], viewport_rect['height']
        x = left + math.floor(width / 2)
        y = top + math.floor(height / 2)
        mobile_adb_tools.swipe(start_x=x, start_y=y, end_x=x, end_y=y + down_value if y + down_value > top else top)
        return self

    def run_click_point(self, x: int, y: int) -> 'AppiumClientTool':
        """
        点击屏幕某个坐标点
        :param x:  坐标x
        :param y: 坐标y
        :return: 当前类，用于链式操作
        """
        mobile_adb_tools.click(x=x, y=y)
        return self

    def run_click(self, by: str, value: str) -> WebElement:
        """
        点击按钮
        :param by: 元素查询条件
        :param value: 查询条件值
        :return: WebElement 点击的元素
        """
        tmp_el = self.driver.find_element(by, value)
        tmp_el.click()
        return tmp_el

    def run_click_elements_one(self, by: str, value: str, index: int) -> WebElement:
        """
        点击按钮集合的第index个
        :param index:
        :param by: 元素查询条件
        :param value: 查询条件值
        @index: 点击元素的索引号
        :return: WebElement 点击的元素
        """
        tmp_el = self.driver.find_elements(by, value)[index]
        tmp_el.click()
        return tmp_el

    def run_wait(self, wait_time: float) -> 'AppiumClientTool':
        """
        等待一些时间
        :param wait_time: 等待的时间：（单位：秒）
        :return: 当前类，用于链式操作
        """
        self.driver.implicitly_wait(wait_time)
        return self

    def run_sleep(self, seconds: float) -> 'AppiumClientTool':
        """
        睡眠一些时间
        :param seconds: 睡眠秒数
        :return: 当前类，用于链式操作
        """
        time.sleep(seconds)
        return self

    def run_wait_element(self, by: str, value: str, timeout: float) -> WebElement:
        """
        等待元素出现
        :param by: 元素查询条件
        :param value: 查询条件值
        :param timeout: 超时时间
        :return: 等待到的元素
        """
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(expected_conditions.presence_of_element_located((by, value)))

    def run_find_element(self, by: str, value: str) -> WebElement:
        """
        查找单个元素
        :param by: 元素查询条件
        :param value: 查询条件值
        :return: WebElement
        """
        return self.driver.find_element(by, value)

    def run_find_elements(self, by: str, value: str) -> List[WebElement]:
        """
        查找多个个元素
        :param by: 元素查询条件
        :param value: 查询条件值
        :return: list[WebElement]
        """
        return self.driver.find_elements(by, value)

    def run_wait_activity(self, activity_name, timeout: int = 3) -> bool:
        """
        等待 activity 加载： 在给定的超时时间内，通过不断轮询Activity的方式，等待指定的Android Activity出现
        :param activity_name: activity名称
        :param timeout: 最大等待时间（单位：秒）
        :return: 是否等待到 activity， False是没有等到，True等到了
        """
        return self.driver.wait_activity(activity_name, timeout)
