#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-06-15
@file:      config.py
@contact:   georgewang1994@163.com
@desc:      flask配置
"""

from enum import Enum

from ammonia.settings import BACKEND_URL, TEST_CASE_BACKEND_URL


class ConfigChoiceEnum(Enum):
    DEVELOPMENT = "dev"  # 线上开发环境
    TEST = "test"  # 测试环境
    TEST_CASE = "test_case"  # 测试用例环境


class _Config(object):
    # @see http://www.pythondoc.com/flask-sqlalchemy/config.html
    # 追踪对象的修改并且发送信号，默认开启
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        pass


class TestConfig(_Config):
    # 连接的数据库
    SQLALCHEMY_DATABASE_URI = BACKEND_URL

    # 显示数据库查询记录
    SQLALCHEMY_RECORD_QUERIES = True


class TestCaseConfig(_Config):
    # 连接的数据库
    SQLALCHEMY_DATABASE_URI = TEST_CASE_BACKEND_URL

    # 显示数据库查询记录
    SQLALCHEMY_RECORD_QUERIES = True


class DevConfig(_Config):
    # 连接的数据库
    SQLALCHEMY_DATABASE_URI = BACKEND_URL


_config = {
    "dev": DevConfig,
    "test": TestConfig,
    "test_case": TestCaseConfig,
}


def get_config(config):
    return _config.get(config, DevConfig)
