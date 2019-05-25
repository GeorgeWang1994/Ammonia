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
from ammonia.utils import generate_random_uid


class TaskManager(object):
    def __init__(self, task_id):
        self.task = registry.task(task_id)

    def to_message(self):
        return {
            "task_id": self.task.task_id,
            "task_name": self.task.task_name,
            "exec_func": self.task.exec_func,
            "args": self.task.args,
            "kwargs": self.task.kwargs,
        }

    def to_task(self, message_data):
        exec_func = message_data.pop("exec_func", None)
        args = message_data.pop("args", ())
        kwargs = message_data.pop("args", {})
        task = Task(exec_func=exec_func, *args, **kwargs)
        return task

    def process_task(self):
        pass


class Task(object):
    def __init__(self, exec_func, *args, **kwargs):
        """
        :param exec_func:
        """
        self.exec_func = exec_func
        self.args = args
        self.kwargs = kwargs
        self.task_id = generate_random_uid()
        self.task_name = str(exec_func) + self.task_id
