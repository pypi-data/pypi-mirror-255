import winreg


def get_desktop_path():
    """获取桌面路径"""
    _key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
    return winreg.QueryValueEx(_key, "Desktop")[0]

print(get_desktop_path())