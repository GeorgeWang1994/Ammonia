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
from ammonia.mq import TaskProducer, TaskConsumer
from ammonia.settings import BROKER_CONNECTION_TIMEOUT, BACKEND_URL
from ammonia.state import TaskStatusEnum
from ammonia.utils import generate_random_uid


class Task(object):
    def __init__(self, exec_func, task_id, *args, **kwargs):
        # 这里的args和kwargs是函数的，而装饰器的参数则是类的参数
        self.args = args
        self.kwargs = kwargs
        self.task_id = task_id
        self.task_name = exec_func.__name__
        self.exec_func = exec_func
        self.backend = default_backend

        self.status = TaskStatusEnum.CREATED.value
        self.result = None

    @property
    def parameter(self):
        return self.args, self.kwargs

    def execute(self):
        return NotImplemented

    @classmethod
    def get_task_producer(cls, channel, routing_key=None):
        return TaskProducer(channel=channel, routing_key=routing_key)

    @classmethod
    def get_task_consumer(cls, channel):
        return TaskConsumer(channel=channel)

    def data(self):
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "exec_func": self.exec_func.__name__,
            "args": self.args,
            "kwargs": self.kwargs,
        }

    def defer_async(self):
        """
        这里的参数是执行函数的参数，延迟执行
        :return:
        """
        with Connection(hostname=BACKEND_URL, connect_timeout=BROKER_CONNECTION_TIMEOUT) as conn:
            routing_key = getattr(self, "routing_key", default=None)
            producer = self.get_task_producer(routing_key=routing_key, channel=conn.channel())
            producer.publish_task(pickle.dumps(self.data()))
            self.status = TaskStatusEnum.PREPARE.value
            return AsyncResult(task_id=self.task_id, backend=self.backend)


class TaskManager(object):
    base_task_class = Task

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.task_class = self.create_task_class(**kwargs)

    def task(self, task_id):
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
        task_id = generate_random_uid()
        return self.process_task(self.task_class(self.func, task_id, *args, **kwargs), True)

    def defer(self, *args, **kwargs):
        task_id = generate_random_uid()
        return self.process_task(self.task_class(self.func, task_id, *args, **kwargs))

    def process_task(self, task, is_immediate=False):
        """
        :param task:
        :param is_immediate: 是否立即执行
        :return:
        """
        task.status = TaskStatusEnum.PREPARE.value
        registry.register(task)
        # 如果是直接调用，则直接计算返回
        if is_immediate:
            return task_trace_execute(task)

        return task.defer_async()

    @classmethod
    def execute_task(cls, pool, task):
        pool.apply_async(task_trace_execute, cls.on_task_success, cls.on_task_fail, task)

    @classmethod
    def on_task_success(cls):
        pass

    @classmethod
    def on_task_fail(cls):
        pass


class TaskTrace(object):
    """
    一个task对应一个trace
    """
    task = None
    result = None

    def __init__(self, task):
        self.task = task

    def execute(self):
        try:
            result = self.do_exec_func()
            self.do_exec_success(result)
            return result
        except Exception as e:
            self.do_exec_fail(e)
            return None

    def do_exec_func(self):
        self.task.status = TaskStatusEnum.PROCESS.value
        self.result = self.task.exec_func(*self.task.args, **self.task.kwargs)
        return self.result

    def do_exec_success(self, return_value):
        self.task.status = TaskStatusEnum.SUCCESS.value
        self.task.backend.mark_task_success(task_id=self.task.task_id, result=return_value)

    def do_exec_fail(self, return_value):
        self.task.status = TaskStatusEnum.FAIL.value
        self.task.backend.mark_task_fail(task_id=self.task.task_id, result=return_value)


def task_trace_execute(task):
    return TaskTrace(task=task).execute()
