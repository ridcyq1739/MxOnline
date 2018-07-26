# -*- coding:utf-8 -*-
__author__ = 'kreg'
__date__ = '2018/6/30 21:52'
from random import Random
from django.core.mail import send_mail
from users.models import EmailVerifyRecord
from MxOnline.settings import EMAIL_FROM


def random_str(random_length=8):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(random_length):
        str += chars[random.randint(0,length)]
    return str


def send_register_email(email,send_type="register"):
    email_record = EmailVerifyRecord()
    if send_type == 'remail':
        code = random_str(4)
    else:
        code = random_str(16)
    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type
    email_record.save()

    email_title = ""
    email_body = ""

    if send_type == "register":
        email_title = "暮雪在线网注册激活链接"
        email_body = "请点击下面的连接激活你的帐号：http://127.0.0.1:8000/active/{0}".format(code)

        send_status = send_mail(email_title,email_body,EMAIL_FROM,[email])

        if send_status:
            pass
    elif send_type == "forget":
        email_title = "暮雪在线网重置密码链接"
        email_body = "请点击下面的连接重置你的密码：http://127.0.0.1:8000/reset/{0}".format(code)

        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])

        if send_status:
            pass

    elif send_type == "remail":
        email_title = "暮雪在线邮箱修改验证码"
        email_body = "你的邮箱验证码为：{0}".format(code)

        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])

        if send_status:
            pass

