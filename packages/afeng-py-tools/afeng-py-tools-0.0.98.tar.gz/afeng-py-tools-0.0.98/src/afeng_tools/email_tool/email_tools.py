"""
邮箱工具
"""
import smtplib

smtp_server_dict = {
    '163': ('smtp.163.com', 25, 465),
    'aliyun': ('smtp.aliyun.com', 25, 465),
    'office365': ('smtp.office365.com', 587, 587)
}


def get_smtp_server_info(email_type: str) -> tuple[str, int, int]:
    """获取smtp服务器信息"""
    return smtp_server_dict.get(email_type)


def login_smtp_server(login_email: str, login_password: str,
                      smtp_host: str = None, smtp_port: int = 25, ssl_smtp_port: int = 465,
                      debug: bool = False, ssl: bool = False) -> smtplib.SMTP | smtplib.SMTP_SSL:
    """
    登录
    """
    if smtp_host is None:
        if login_email.endswith('@aliyun.com'):
            smtp_host, smtp_port, ssl_smtp_port = get_smtp_server_info('aliyun')
        if login_email.endswith('@163.com'):
            smtp_host, smtp_port, ssl_smtp_port = get_smtp_server_info('163')
    if ssl:
        # SMTP协议默认端口是25
        server = smtplib.SMTP_SSL(smtp_host, ssl_smtp_port)
    else:
        # SMTP协议默认端口是25
        server = smtplib.SMTP(smtp_host, smtp_port)
    # login()方法用来登录SMTP服务器
    server.login(login_email, login_password)
    if debug:
        # 打印出和SMTP服务器交互的所有信息。
        server.set_debuglevel(1)
    return server
