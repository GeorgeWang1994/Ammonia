#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-24
@file:      ammonia.py
@contact:   georgewang1994@163.com
@desc:      总控制
"""

from ammonia import settings
from ammonia.backends.backend import get_backend_by_settings
from ammonia.base.task import TaskManager

# 默认配置
DEFAULT_CONF = {
    "DEBUG": False,
    "TASK_URL": settings.get_task_url(),
    "BACKEND_URL": settings.get_backend_url(),
    "BACKEND_TYPE": "database",
    "TASK_CONNECTION_TIMEOUT": settings.TASK_CONNECTION_TIMEOUT,
    "BACKEND_CONNECTION_TIMEOUT": settings.BACKEND_CONNECTION_TIMEOUT,
}


class Ammonia(object):
    conf = DEFAULT_CONF
    backend = None

    def __init__(self, conf=None):
        if conf:
            self.conf.update(conf)

        backend_cls = get_backend_by_settings(self.conf["BACKEND_TYPE"])
        self.backend = backend_cls(self.conf["BACKEND_URL"])

    @classmethod
    def task(cls, *args, **kwargs):
        """
        task装饰器，创建task任务
        :param args:
        :param kwargs:
        :return:
        """
        def decorator(func):
            return TaskManager.create_task(func, *args, **kwargs)
        return decorator

    @classmethod
    def create_package(cls, name, *args, **kwargs):
        """
        创建任务package
        :param name:
        :return:
        """
        return TaskManager.create_task_package(name, *args, **kwargs)

    def update_conf(self, conf={}):
        return self.conf.update(conf)

    def get_conf(self):
        return self.conf

    def _check_conf(self):
        # todo: 检查配置是否正确
        pass
