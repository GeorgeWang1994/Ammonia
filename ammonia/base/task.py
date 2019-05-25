#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-24
@file:      task.py
@contact:   georgewang1994@163.com
@desc:      任务相关的类
"""

from ammonia.base.registry import registry
from ammonia.base.result import AsyncResult


class Task(object):
    def __init__(self, task_id, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.task_id = task_id

    @property
    def parameter(self):
        return self.args, self.kwargs

    def execute(self):
        return NotImplemented


class TaskManager(object):
    base_task_class = Task

    def __init__(self, task_id, func, *args, **kwargs):
        self.task_id = task_id
        self.func = func
        self.task_class = self.create_task_class(**kwargs)

    @classmethod
    def task(cls, task_id):
        try:
            task = registry.task(task_id)
        except KeyError:
            raise KeyError("未找到 %s 对应的任务" % task_id)
        return task

    @classmethod
    def to_message(cls, task):
        return {
            "task_id": task.task_id,
            "task_name": task.task_name,
            "exec_func": task.exec_func,
            "args": task.args,
            "kwargs": task.kwargs,
        }

    @classmethod
    def to_task(cls, message_data):
        exec_func = message_data.pop("exec_func", None)
        args = message_data.pop("args", ())
        kwargs = message_data.pop("args", {})
        task = Task(exec_func=exec_func, *args, **kwargs)
        return task

    def create_task_class(self, **kwargs):
        execute_func = self.func

        def execute(self):
            args, kwargs = self.parameter
            execute_func(*args, **kwargs)

        settings = {
            'task_id': self.task_id,
            'execute': execute,
            '__doc__': execute_func.__doc__,
            '__module': execute_func.__module__,
        }
        settings.update(kwargs)
        return type(self.func.__name__, (self.base_task_class,), settings)

    def __call__(self, *args, **kwargs):
        return self.process_task(self.task_class(self.task_id, *args, *kwargs))

    def process_task(self, task):
        registry.register(task)
        return AsyncResult(task.task_id)
