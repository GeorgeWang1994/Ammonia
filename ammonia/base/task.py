#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-24
@file:      task.py
@contact:   georgewang1994@163.com
@desc:      任务相关的类
"""

import pickle

from kombu import Connection

from ammonia.backends.backend import default_backend
from ammonia.base.registry import registry
from ammonia.base.result import AsyncResult
from ammonia.settings import BROKER_CONNECTION_TIMEOUT, BACKEND_URL
from ammonia.utils import generate_random_uid
from ammonia.worker.mq import TaskProducer, TaskConsumer


class Task(object):
    def __init__(self, exec_func, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.task_id = generate_random_uid()
        self.task_name = exec_func.__name__
        self.exec_func = exec_func
        self.backend = default_backend

    @property
    def parameter(self):
        return self.args, self.kwargs

    def execute(self):
        return NotImplemented

    @classmethod
    def get_producer(cls, channel, routing_key=None):
        return TaskProducer(routing_key=routing_key, channel=channel)

    @classmethod
    def get_consumer(cls, channel):
        return TaskConsumer(channel=channel)

    def data(self):
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "exec_func": self.exec_func.__name__,
            "args": self.args,
            "kwargs": self.kwargs,
        }

    def _defer_async(self, *args, **kwargs):
        """
        这里的参数是执行函数的参数
        :param args:
        :param kwargs:
        :return:
        """
        with Connection(hostname=BACKEND_URL, connect_timeout=BROKER_CONNECTION_TIMEOUT) as conn:
            routing_key = self.routing_key
            producer = self.get_producer(routing_key=routing_key, channel=conn.channel())
            producer.publish_task(pickle.dumps(self.data()))
            return AsyncResult(task_id=self.task_id, backend=self.backend)

    def defer(self, *args, **kwargs):
        return self._defer_async(*args, **kwargs)


class TaskManager(object):
    base_task_class = Task

    def __init__(self, func, *args, **kwargs):
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
    def to_message(self, task):
        return task.data()

    @classmethod
    def to_task(cls, message_data):
        exec_func = message_data.pop("exec_func", None)
        if not exec_func:
            raise KeyError("不存在任务队列的执行函数")
        args = message_data.pop("args", ())
        kwargs = message_data.pop("kwargs", {})
        task = Task(exec_func=exec_func, *args, **kwargs)
        return task

    def create_task_class(self, **kwargs):
        execute_func = self.func

        def execute(self):
            args, kwargs = self.parameter
            execute_func(*args, **kwargs)

        settings = {
            'execute': execute,
            '__doc__': execute_func.__doc__,
            '__module': execute_func.__module__,
        }
        # 将执行函数的参数和装饰器的参数合并到一块
        settings.update(kwargs)
        return type(self.func.__name__, (self.base_task_class,), settings)

    def __call__(self, *args, **kwargs):
        return self.process_task(self.task_class(self.func, *args, **kwargs))

    def defer(self, *args, **kwargs):
        return self.process_task(self.task_class(self.func, *args, **kwargs))

    def process_task(self, task):
        registry.register(task)
        return task.defer()
