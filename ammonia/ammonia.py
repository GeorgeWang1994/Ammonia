#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-24
@file:      ammonia.py
@contact:   georgewang1994@163.com
@desc:      总控制
"""

from functools import wraps

from ammonia.worker.controller import WorkerController
from ammonia.base.task import Task


class Ammonia(object):

    def __init__(self):
        self.worker_controller = WorkerController()

    def run(self):
        self.worker_controller.start()

    @classmethod
    def task(cls, *task_args, **task_kwargs):
        def decorator(func):
            @wraps
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            task = Task(exec_func=func, )
            task.__module__ = func.__module__
            task.__doc__ = func.__doc__
            return wrapper
        return decorator


ammonia = Ammonia()

if __name__ == '__main__':
    ammonia.run()
