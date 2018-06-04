# encoding: utf-8

import os
from datetime import timedelta

SECRET_KEY = os.urandom(24)  # 设置session的secret key

PERMANENT_SESSION_LIFETIME = timedelta(hours=10)  # 设置session内存的东西可以保持10小时，即账户能保持10小时登录

# MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 设置请求内容的大小限制，即限制了上传文件的大小

DEBUG = True

# APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
# APP_STATIC_TXT = os.path.join(APP_ROOT, 'static')  # 设置一个专门的类似全局变量的东西
