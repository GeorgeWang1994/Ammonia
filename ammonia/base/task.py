#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-24
@file:      task.py
@contact:   georgewang1994@163.com
@desc:      任务相关的类
"""

import random

from ammonia import settings
from ammonia.backends.backend import default_backend
from ammonia.base.registry import registry
from ammonia.base.result import AsyncResult
from ammonia.mq import TaskProducer, TaskConnection, task_exchange, task_queues
from ammonia.state import TaskStatusEnum
from ammonia.utils import generate_random_uid


class Task(object):
    def __init__(self, task_id, *args, **kwargs):
        # 这里的args和kwargs是函数的，而装饰器的参数则是类的参数
        self.args = args
        self.kwargs = kwargs
        self.task_id = task_id
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
        return TaskProducer(channel=channel, routing_key=routing_key, exchange=task_exchange, serializer='json')

    def data(self):
        return {
            "task_id": self.task_id,
            "args": self.args,
            "kwargs": self.kwargs,
        }

    def defer_async(self):
        """
        这里的参数是执行函数的参数，延迟执行
        :return:
        """
        with TaskConnection() as conn:
            routing_key = getattr(self, "routing_key", "")
            if not routing_key:
                routing_key = random.choice(settings.TASK_ROUTING_KEY_LIST)
            print("发送消息给路由%s %s" % (routing_key, self.data()))
            producer = self.get_task_producer(channel=conn, routing_key=routing_key)
            producer.publish_task(self.data(), routing_key=routing_key,
                                  exchange=task_exchange, declare=task_queues)
            self.status = TaskStatusEnum.PREPARE.value
            return AsyncResult(task_id=self.task_id, backend=self.backend)


class TaskManager(object):
    base_task_class = Task

    def __init__(self, func, *args, **kwargs):
        self.execute_func = func
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
        return task.data()

    def _get_task_execute_func(self):
        execute_func = self.execute_func

        def execute(self):
            args, kwargs = self.parameter
            return execute_func(*args, **kwargs)

        return execute

    def create_task_class(self, **kwargs):
        execute_func = self.execute_func

        task_execute_func = self._get_task_execute_func()

        task_settings = {
            'execute': task_execute_func,
            '__doc__': execute_func.__doc__,
            '__module': execute_func.__module__,
        }
        # 将执行函数的参数和装饰器的参数合并到一块
        task_settings.update(kwargs)
        return type('Task', (self.base_task_class,), task_settings)

    def __call__(self, *args, **kwargs):
        task_id = generate_random_uid()
        return self.process_task(self.task_class(task_id, *args, **kwargs), True)

    def defer(self, *args, **kwargs):
        task_id = generate_random_uid()
        return self.process_task(self.task_class(task_id, *args, **kwargs))

    def process_task(self, task, is_immediate=False):
        """
        :param task:
        :param is_immediate: 是否立即执行
        :return:
        """
        print("是否执行到了这里...")
        task.status = TaskStatusEnum.PREPARE.value
        # todo: 客户端和服务器维护的registry不一致
        registry.register(task)
        print("cache is %s" % registry.cache)
        # 如果是直接调用，则直接计算返回
        if is_immediate:
            return task_trace_execute(task)

        return task.defer_async()

    @classmethod
    async def execute_task(cls, pool, task):
        await pool.apply_async(task_trace_execute, cls.on_task_success, cls.on_task_fail, task)

    @classmethod
    def on_task_success(cls, return_value):
        print("任务执行成功，返回结果为%s" % return_value)

    @classmethod
    def on_task_fail(cls, return_value):
        print("任务执行失败，返回结果为%s" % return_value)


class TaskTrace(object):
    """
    一个task对应一个trace
    """
    task = None
    result = None

    def __init__(self, task):
        self.task = task

    def execute(self):
        print("任务开始执行...")
        try:
            result = self.do_exec_func()
            print("任务执行成功, %s" % result)
            self.do_exec_success(result)
            return result
        except Exception as e:
            print("任务执行失败, %s" % e)
            self.do_exec_fail(e)
            return None

    def do_exec_func(self):
        self.task.status = TaskStatusEnum.PROCESS.value
        self.result = self.task.execute()
        return self.result

    def do_exec_success(self, return_value):
        self.task.status = TaskStatusEnum.SUCCESS.value
        self.task.backend.mark_task_success(task_id=self.task.task_id, result=return_value)

    def do_exec_fail(self, return_value):
        self.task.status = TaskStatusEnum.FAIL.value
        self.task.backend.mark_task_fail(task_id=self.task.task_id, result=return_value)


def task_trace_execute(task):
    return TaskTrace(task=task).execute()
