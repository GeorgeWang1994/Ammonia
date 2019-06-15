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
BACKEND_PORT = "3306"

# 数据库端用户名
BACKEND_USER = "root"

# 数据库端密码
BACKEND_PASSWORD = "123456"

# 数据库编码
BACKEND_ENCODING = "utf-8"

# 数据库名字
BACKEND_NAME = "ammonia"

# 数据信息（数据库类型+数据库驱动名称）
BACKEND_TYPE = "mysql+pymysql"


def get_backend_url(type=BACKEND_TYPE, user=BACKEND_USER, password=BACKEND_PASSWORD,
                    host=BACKEND_HOSTNAME, port=BACKEND_PORT, db_name=BACKEND_NAME):
    return "{type}://{user}:{password}@{host}:{port}/{db_name}".format(
        type=type, user=user, password=password, host=host,
        port=port, db_name=db_name
    )


# 数据库URL(数据库类型+数据库驱动名称://用户名:口令@机器地址:端口号/数据库名)
BACKEND_URL = get_backend_url()

# 测试用例的数据库名字
TEST_CASE_BACKEND_NAME = f"test_{BACKEND_NAME}"

# 测试用例数据库URL
TEST_CASE_BACKEND_URL = get_backend_url(db_name=TEST_CASE_BACKEND_NAME)

# 连接超时时间
BROKER_CONNECTION_TIMEOUT = 3
