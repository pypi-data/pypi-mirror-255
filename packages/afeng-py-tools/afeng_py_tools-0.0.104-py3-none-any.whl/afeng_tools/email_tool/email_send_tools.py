"""
发送邮箱工具
"""
import email
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

from afeng_tools.http_tool import http_mimetype_tools
from afeng_tools.log_tool.loguru_tools import get_logger, log_error

log = get_logger()


def send_email(smtp_client: smtplib.SMTP_SSL, from_nickname: str, from_email: str, receiver_list: list[str],
               subject: str, email_content: str, is_html: bool = True, cc_list: list[str] = None,
               bcc_list: list[str] = None,
               image_attachments: dict[str, str] = None, file_attachments: dict[str, str] = None):
    if is_html:
        email_msg = MIMEText(email_content, 'html', 'utf-8')
    else:
        email_msg = MIMEText(email_content, 'plain', 'utf-8')
    if image_attachments or file_attachments:
        multi_email_msg = MIMEMultipart()
        multi_email_msg.attach(email_msg)
        email_msg = multi_email_msg
    # 发送者
    email_msg['From'] = formataddr(pair=(from_nickname, from_email))
    # 发送多人邮件写法
    email_msg['To'] = ','.join(receiver_list)
    if cc_list:
        # 抄送
        email_msg['Cc'] = ','.join(cc_list)
    if bcc_list:
        # 密送：建议密送地址在邮件头中隐藏
        # email_msg['Bcc'] = ','.join(bcc_list)
        pass
    email_msg['Message-id'] = email.utils.make_msgid()
    email_msg['Date'] = email.utils.formatdate()
    # 主题
    email_msg['Subject'] = subject
    if image_attachments:
        for cid, local_file in image_attachments.items():
            if os.path.exists(local_file):
                with open(local_file, 'rb') as img_f:
                    msg_img = MIMEImage(img_f.read())
                    msg_img.add_header('Content-ID', cid)
                    email_msg.attach(msg_img)
    if file_attachments:
        for file_name, local_file in file_attachments.items():
            if os.path.exists(local_file):
                with open(local_file, 'rb') as tmp_f:
                    attachment_msg = MIMEApplication(tmp_f.read())
                    attachment_msg["Content-Type"] = http_mimetype_tools.get_mimetype(local_file)[0]
                    attachment_msg.add_header('Content-Disposition', 'attachment', filename=('utf-8', '', file_name))
                    email_msg.attach(attachment_msg)
    try:
        rcpt_to = receiver_list
        if cc_list:
            rcpt_to.extend(cc_list)
        if bcc_list:
            rcpt_to.extend(bcc_list)
        send_result = smtp_client.sendmail(from_email, rcpt_to, email_msg.as_string())
        print('Email Send Success', send_result)
    except Exception as e:
        log_error(log, 'Email Send Failure', e)
    finally:
        if smtp_client:
            smtp_client.quit()


def send_html_email(smtp_client: smtplib.SMTP_SSL, from_nickname: str, from_email: str, receiver_list: list[str],
                    subject: str, email_content: str):
    try:

        # 发送纯文本格式的邮件
        email_msg = MIMEText(email_content, 'html', 'utf-8')
        # 发送者
        email_msg['From'] = formataddr(pair=(from_nickname, from_email))
        # 发送多人邮件写法
        email_msg['To'] = ','.join(receiver_list)
        # 主题
        email_msg['Subject'] = subject
        send_result = smtp_client.sendmail(from_email, receiver_list, email_msg.as_string())
        print('Email Send Success', send_result)
    except Exception as e:
        log_error(log, 'Email Send Failure', e)
    finally:
        if smtp_client:
            smtp_client.quit()


if __name__ == '__main__':
    pass
    # smtp_server = email_tools.login_smtp_server(login_email='chentiefeng521@163.com', login_password='PREYPKZJRVEJAVAH', ssl=True)
    # send_email(smtp_server, from_nickname='陈铁锋', from_email='chentiefeng521@163.com',
    #                 receiver_list=['imchentiefeng@aliyun.com', 'imchentiefeng@163.com'],
    #                 subject='hello，i just want to test',
    #                 email_content="<html><h1>人生苦短，何必执着</h1></html>", cc_list=['afenghome@aliyun.com'], bcc_list=['afengbook@aliyun.com'])
    # smtp_server = email_tools.login_smtp_server(login_email='afenghome@aliyun.com', login_password='Tie%007+521aly')
    # send_email(smtp_server, from_nickname='陈铁锋', from_email='afenghome@aliyun.com',
    #            receiver_list=['afengbook@aliyun.com'],
    #            subject='hello，i just want to test',
    #            email_content='<html><h1>人生苦短，何必执着</h1><br/><img src="cid:test" alt="logo" width="500" height="200"></html>',
    #            image_attachments={
    #                'test': r'C:\BaiduNetdiskWorkspace\教程\小程序\微信小程序\images\微信小程序开发指南\image-20231119042219753.png'},
    #            file_attachments={
    #                '小程序 - 视图与逻辑.pptx': r'C:\Users\chentiefeng\Downloads\3. 手把手教你微信小程序\微信小程序基础\微信小程序基础-资料\day03\讲义（ppt）\00_小程序 - 视图与逻辑.pptx'})
