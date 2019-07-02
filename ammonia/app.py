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

    def __init__(self, conf=None):
        if conf:
            self.conf.update(conf)

    @classmethod
    def task(cls, *args, **kwargs):
        def decorator(func):
            return TaskManager.create_task(func, *args, **kwargs)
        return decorator

    def update_conf(self, conf={}):
        return self.conf.update(conf)

    def get_conf(self):
        return self.conf

    def _check_conf(self):
        # todo: 检查配置是否正确
        pass
