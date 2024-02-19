import os
import re

from afeng_tools.appium_tool.mobile_keycode import MobileKeycode


def get_devices_info():
    """获取所有连接设备"""
    output = os.popen('adb devices -l')
    device_list = []
    for tmp_line in output.readlines()[1:]:
        if tmp_line.strip():
            tmp_info_list = list(filter(lambda x: x != '', tmp_line.strip().split(' ')))
            device_list.append({
                'id': tmp_info_list[0],
                'product': tmp_info_list[2].split(':')[1],
                'model': tmp_info_list[3].split(':')[1],
                'device': tmp_info_list[4].split(':')[1],
                'transport_id': tmp_info_list[5].split(':')[1],
            })
    return device_list


def get_device_name():
    """获取第一个连接设备的名称"""
    devices_list = get_devices_info()
    if devices_list:
        return devices_list[0]['product']


def get_platform_version():
    """获取安卓版本"""
    output = os.popen("adb shell getprop ro.build.version.release").read()
    if output:
        return output.strip()


def get_current_activity() -> tuple:
    """
    获取当前Activity
    :return: (app_package, app_activity)
    使用示例：app_package, app_activity = get_current_activity()
    """
    output = os.popen('adb shell dumpsys activity | findstr "mResume"').read()
    if output:
        activity_record_obj_str = output.strip().split(':')[1].strip()
        re_match = re.match('^ActivityRecord\\{\w* \w* (\S*)/(\S*) \w*\\}$', activity_record_obj_str)
        if re_match:
            return re_match.group(1), re_match.group(2)


def send_keys(text):
    """输入文本"""
    os.popen(f'adb shell input text {text}').read()


def swipe(start_x, start_y, end_x, end_y) -> None:
    """
    滑动屏幕
    :param start_x: 开始点x坐标
    :param start_y: 开始点y坐标
    :param end_x: 结束点x坐标
    :param end_y: 结束点y坐标
    :return: None
    """
    os.popen(f'adb shell input swipe {start_x} {start_y} {end_x} {end_y}').read()


def click(x, y) -> None:
    """
    点击屏幕
    :param x: x坐标
    :param y: y坐标
    :return: None
    """
    os.popen(f'adb shell input tap {x} {y}').read()


def press_key(mobile_key: MobileKeycode):
    os.popen(f'adb shell input keyevent {mobile_key.value}').read()


def open_tcpip_port(port: int):
    """打开tcpip端口"""
    os.popen(f'adb tcpip {port}')


def connect_device(ip: str, port: int):
    """连接设备"""
    os.popen(f'adb connect {ip}:{port}')


def open_app(app_package: str, app_activity: str):
    """
    打开app
    :param app_package: 要打开的应用包名
    :param app_activity: 要打开的Activity
    :return:
    """
    os.popen(f'adb shell am start -n {app_package}/{app_activity}')


def get_point():
    """获取手机点击坐标"""
    output = os.popen(f'adb shell getevent -p').read()
    print(output)


def get_press_key():
    """查看点击按键"""
    output = os.popen(f'adb shell getevent -t').read()
    print(output)


if __name__ == '__main__':
    print(get_device_name())  # PCT-AL10
    # app_package, app_activity = get_current_activity()
    # print(app_package)
    # print(app_activity)
    print(get_platform_version())
    # press_key(MobileKeycode.KEYCODE_BACK)
    # get_point()
    pass
