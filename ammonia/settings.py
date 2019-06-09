#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-12
@file:      settings.py
@contact:   georgewang1994@163.com
@desc:      配置文件
"""


# 是否正在调试
DEBUG = True

# 数据库主机名
BACKEND_HOSTNAME = "localhost"

# 数据库端口号
BACKEND_PORT = "5672"

# 数据库端用户名
BACKEND_USER = "guest"

# 数据库端密码
BACKEND_PASSWORD = "guest"

# 数据库编码
BACKEND_ENCODING = "utf-8"

# 数据库名字
BACKEND_NAME = ""

# 数据信息（数据库类型+数据库驱动名称）
BACKEND_TYPE = "amqp"

# 数据库URL(数据库类型+数据库驱动名称://用户名:口令@机器地址:端口号/数据库名)
BACKEND_URL = "{type}://{user}:{password}@{host}:{port}//{db_name}".format(
    type=BACKEND_TYPE, user=BACKEND_USER, password=BACKEND_PASSWORD,
    host=BACKEND_HOSTNAME, port=BACKEND_PORT, db_name=BACKEND_NAME
)

# 连接超时时间
BROKER_CONNECTION_TIMEOUT = 3
