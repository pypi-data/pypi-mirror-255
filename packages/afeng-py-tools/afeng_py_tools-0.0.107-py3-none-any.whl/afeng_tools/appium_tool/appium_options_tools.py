from appium.options.common import AppiumOptions

from afeng_tools.appium_tool.mobile_adb_tools import get_platform_version, get_device_name


def huawei_options(app_package:str, app_activity:str) -> AppiumOptions:
    desired_caps = {
        'platformName': 'Android',
        'platformVersion': get_platform_version(),  # '10'
        'deviceName': get_device_name(),  # 'PCT-AL10'
        'appPackage': app_package,
        'appActivity': app_activity,
        "noReset": True,
        'ensureWebviewsHavePages': True,
        'nativeWebScreenshot': True,
        'newCommandTimeout': 3600,  # 设置超时时间， 默认为60s,设置为0关闭。超时时间到后，软件将退出
        'connectHardwareKeyboard': True,
        # 'automationName': 'Uiautomator2'
    }
    return AppiumOptions().load_capabilities(desired_caps)