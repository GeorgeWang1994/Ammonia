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
from ammonia.base.registry import task_registry
from ammonia.base.result import AsyncResult
from ammonia.mq import TaskProducer, TaskConnection, task_exchange, task_queues
from ammonia.state import TaskStatusEnum
from ammonia.utils import generate_random_uid


class Task(object):
    def __init__(self, task_id, *args, **kwargs):
        # 这里的args和kwargs是函数的，而装饰器的参数则是类的参数
        self.task_id = task_id
        self.status = TaskStatusEnum.CREATED.value
        self.routing_key = getattr(self, "routing_key", "")

        self.backend = default_backend
        self.result = None

    def execute(self):
        return NotImplemented

    @classmethod
    def get_task_producer(cls, channel, routing_key=None):
        return TaskProducer(channel=channel, routing_key=routing_key, exchange=task_exchange, serializer='json')

    def data(self):
        return {
            "task_id": self.task_id,
            "status": self.status,
            "routing_key": self.routing_key,
        }

    def defer_async(self, *args, **kwargs):
        """
        这里的参数是执行函数的参数，延迟执行
        :return:
        """
        with TaskConnection() as conn:
            # 如果路由不存在则随机路由
            if not self.routing_key:
                self.routing_key = random.choice(settings.TASK_ROUTING_KEY_LIST)
            print("发送消息给路由%s %s" % (self.routing_key, self.data()))
            producer = self.get_task_producer(channel=conn, routing_key=self.routing_key)
            data = self.data()
            data.update({
                "args": args,
                "kwargs": kwargs,
            })
            producer.publish_task(data, routing_key=self.routing_key,
                                  exchange=task_exchange, declare=task_queues)
            return AsyncResult(task_id=self.task_id, backend=self.backend)

    def __call__(self, *args, **kwargs):
        return self._process_task(True, *args, **kwargs)

    def defer(self, *args, **kwargs):
        return self._process_task(False, *args, **kwargs)

    def _process_task(self, is_immediate=False, *args, **kwargs):
        """
        :param task:
        :param is_immediate: 是否立即执行
        :return:
        """
        self.status = TaskStatusEnum.PREPARE.value
        # 如果是直接调用，则直接计算返回
        if is_immediate:
            return task_trace_execute(self, *args, **kwargs)

        return self.defer_async(*args, **kwargs)


class TaskManager(object):
    base_task_class = Task

    def __init__(self, task_id, *args, **kwargs):
        self.task_id = task_id

    @classmethod
    def to_message(cls, task):
        return task.data()

    @classmethod
    def _get_task_execute_func(cls, execute_func):

        def execute(self, *args, **kwargs):
            return execute_func(*args, **kwargs)

        return execute

    @classmethod
    def create_task_class(cls, execute_func, **kwargs):

        task_execute_func = cls._get_task_execute_func(execute_func)

        task_settings = {
            'execute': task_execute_func,
            '__doc__': execute_func.__doc__,
            '__module': execute_func.__module__,
        }
        # 将执行函数的参数和装饰器的参数合并到一块
        task_settings.update(kwargs)

        return type(execute_func.__name__, (TaskManager.base_task_class,), task_settings)

    @classmethod
    def create_task(cls, execute_func, *args, **kwargs):
        task_id = generate_random_uid()
        task_cls = cls.create_task_class(execute_func)
        task = task_cls(task_id, *args, **kwargs)
        task_registry.register(task)
        return task

    @classmethod
    async def execute_task(cls, pool, task, *args, **kwargs):
        await pool.apply_async(task_trace_execute, cls.on_task_success, cls.on_task_fail, task, *args, **kwargs)

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

    def execute(self, *args, **kwargs):
        print("任务开始执行...")
        try:
            result = self.do_exec_func(*args, **kwargs)
            print("任务执行成功, %s" % result)
            self.do_exec_success(result)
            return result
        except Exception as e:
            print("任务执行失败, %s" % e)
            self.do_exec_fail(e)
            return None

    def do_exec_func(self, *args, **kwargs):
        self.task.status = TaskStatusEnum.PROCESS.value
        self.result = self.task.execute(*args, **kwargs)
        return self.result

    def do_exec_success(self, return_value):
        self.task.status = TaskStatusEnum.SUCCESS.value
        self.task.backend.mark_task_success(task_id=self.task.task_id, result=return_value)

    def do_exec_fail(self, return_value):
        self.task.status = TaskStatusEnum.FAIL.value
        self.task.backend.mark_task_fail(task_id=self.task.task_id, result=return_value)


def task_trace_execute(task, *args, **kwargs):
    return TaskTrace(task=task).execute(*args, **kwargs)
