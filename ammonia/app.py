#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-24
@file:      ammonia.py
@contact:   georgewang1994@163.com
@desc:      总控制
"""

from ammonia.base.task import TaskManager


class Ammonia(object):
    @staticmethod
    def task(*args, **kwargs):
        def decorator(func):
            return TaskManager.create_task(func, *args, **kwargs)
        return decorator
