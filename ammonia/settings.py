#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-12
@file:      settings.py
@contact:   georgewang1994@163.com
@desc:      配置文件
"""

import os


# 是否正在调试
DEBUG = False

# 存储的主机名
BACKEND_HOSTNAME = "localhost"

# 存储的端口号
BACKEND_PORT = "3306"

# 存储的用户名
BACKEND_USER = "root"

# 存储的密码
BACKEND_PASSWORD = "123456"

# 存储的数据库名字
BACKEND_NAME = "ammonia"

# 数据信息（数据库类型+数据库驱动名称）
BACKEND_TYPE = "mysql+pymysql"


# 连接超时时间
BACKEND_CONNECTION_TIMEOUT = 3


def get_backend_url(type=BACKEND_TYPE, user=BACKEND_USER, password=BACKEND_PASSWORD,
                    host=BACKEND_HOSTNAME, port=BACKEND_PORT, db_name=BACKEND_NAME):
    return f"{type}://{user}:{password}@{host}:{port}/{db_name}"


# 数据库URL(数据库类型+数据库驱动名称://用户名:口令@机器地址:端口号/数据库名)
BACKEND_URL = get_backend_url()

# 测试用例的数据库名字
TEST_CASE_BACKEND_NAME = f"test_{BACKEND_NAME}"

# 测试用例数据库URL
TEST_CASE_BACKEND_URL = get_backend_url(db_name=TEST_CASE_BACKEND_NAME)

# 连接超时时间
TASK_CONNECTION_TIMEOUT = 3


# 任务队列的主机名
TASK_HOSTNAME = "localhost"

# 任务队列的端口号
TASK_PORT = "5672"

# 任务队列的用户名
TASK_USER = "guest"

# 任务队列的密码
TASK_PASSWORD = "guest"

# 数据信息
TASK_TYPE = "amqp"


# 任务队列的地址
TASK_URL = f"{TASK_TYPE}://{TASK_USER}:{TASK_PASSWORD}@{TASK_HOSTNAME}:{TASK_PORT}//"


def get_task_url(type=TASK_TYPE, user=TASK_USER, password=TASK_PASSWORD,
                 host=TASK_HOSTNAME, port=TASK_PORT):
    return f"{type}://{user}:{password}@{host}:{port}//"


# 任务队列名
HIGH_TASK_QUEUE_NAME = "high_task"
MID_TASK_QUEUE_NAME = "mid_task"
LOW_TASK_QUEUE_NAME = "low_task"

# 任务队列路由key
HIGH_TASK_ROUTING_KEY = "high_queue"
MID_TASK_ROUTING_KEY = "mid_queue"
LOW_TASK_ROUTING_KEY = "low_queue"

TASK_ROUTING_KEY_LIST = [HIGH_TASK_ROUTING_KEY, MID_TASK_ROUTING_KEY, LOW_TASK_ROUTING_KEY]

# 任务交换器名字
TASK_EXCHANGE_NAME = "task"


# 项目路径
BASE_PROJECT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# 获取任务模块的后缀名
TASK_MODULE_SUFFIX = "tasks"

# 是否是测试用例
IS_FOR_TEST_CASE = False
