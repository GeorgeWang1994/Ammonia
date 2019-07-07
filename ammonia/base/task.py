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
import sys

from ammonia import settings
from ammonia.base.registry import task_registry
from ammonia.base.result import AsyncResult
from ammonia.mq import TaskProducer, TaskConnection, task_exchange, task_queues
from ammonia.state import TaskStatusEnum


class Task(object):
    def __init__(self, task_id, backend, *args, **kwargs):
        # 这里的args和kwargs是函数的，而装饰器的参数则是类的参数
        self.task_id = task_id
        self.status = TaskStatusEnum.CREATED.value
        self.routing_key = getattr(self, "routing_key", "")
        self.retry = getattr(self, "retry", 0)
        self.backend = backend
        self.result = None

    def execute(self):
        raise NotImplemented

    @classmethod
    def get_task_producer(cls, channel, routing_key=None):
        return TaskProducer(channel=channel, routing_key=routing_key, exchange=task_exchange, serializer='json')

    def data(self):
        return {
            "task_id": self.task_id,
            "status": self.status,
            "routing_key": self.routing_key,
            "retry": self.retry,
        }

    def defer_async(self, *args, **kwargs):
        """
        这里的参数是执行函数的参数，延迟执行
        :return:
        """
        from ammonia.app import Ammonia
        with TaskConnection(hostname=Ammonia.conf["TASK_URL"],
                            connect_timeout=Ammonia.conf["TASK_CONNECTION_TIMEOUT"]) as conn:
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

    def __str__(self):
        return "task[%s-%s]" % (self.task_id, self.status)

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


class TaskPackage(object):
    """
    将task都封装到package中，用于执行一系列任务
    """
    def __init__(self, package_name, backend, *args, **kwargs):
        self.package_name = package_name
        self.status = TaskStatusEnum.CREATED.value
        self.routing_key = getattr(self, "routing_key", "")
        self.retry = getattr(self, "retry", 0)
        self.backend = backend
        self.result = None  # 取最后一个任务的结果
        self.task_list = []

    def register(self, task):
        if not task or task in self.task_list:
            return

        self.task_list.append(task)

    @classmethod
    def get_task_producer(cls, channel, routing_key=None):
        return TaskProducer(channel=channel, routing_key=routing_key, exchange=task_exchange, serializer='json')

    def data(self):
        return {
            "package_name": self.package_name,
            "status": self.status,
            "routing_key": self.routing_key,
            "retry": self.retry,
        }

    def defer_async(self, *args):
        """
        由于是package，因此里面的参数则是以列表的形式，比如((1,2), ('a', 'b'))
        因此这里参数列表需要和任务列表的顺序保持一致
        :return:
        """
        from ammonia.app import Ammonia
        with TaskConnection(hostname=Ammonia.conf["TASK_URL"],
                            connect_timeout=Ammonia.conf["TASK_CONNECTION_TIMEOUT"]) as conn:
            # 如果路由不存在则随机路由
            if not self.routing_key:
                self.routing_key = random.choice(settings.TASK_ROUTING_KEY_LIST)
            print("发送消息给路由%s %s" % (self.routing_key, self.data()))
            producer = self.get_task_producer(channel=conn, routing_key=self.routing_key)
            data = self.data()
            data.update({
                "args": args,
            })
            producer.publish_task(data, routing_key=self.routing_key,
                                  exchange=task_exchange, declare=task_queues)
            return AsyncResult(task_id=self.package_name, backend=self.backend)

    def __call__(self, *args, **kwargs):
        return self._process_task(True, *args)

    def __str__(self):
        return "package[%s-%s]" % (self.package_name, self.status)

    def defer(self, *args):
        return self._process_task(False, *args)

    def _process_task(self, is_immediate=False, *args):
        """
        :param task:
        :param is_immediate: 是否立即执行
        :return:
        """
        if not self.task_list:
            raise Exception("任务包中的任务为空")

        if len(self.task_list) <= 1:
            raise Exception("任务包中任务个数至少为两个")

        self.status = TaskStatusEnum.PREPARE.value
        # 如果是直接调用，则直接计算返回
        if is_immediate:
            return package_trace_execute(self, *args)

        return self.defer_async(*args)


class TaskManager(object):
    base_task_class = Task
    base_package_class = TaskPackage

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

        return type(execute_func.__name__, (cls.base_task_class,), task_settings)

    @classmethod
    def create_task(cls, execute_func, backend, *args, **kwargs):
        task_module = sys.modules[execute_func.__module__]
        task_id = ".".join([task_module.__name__, execute_func.__name__, ])
        task_cls = cls.create_task_class(execute_func, **kwargs)
        task = task_cls(task_id, backend, *args, **kwargs)
        task_registry.register(task)

        # 如果填写了package的话，需要注册到package
        if kwargs.get("package"):
            if isinstance(kwargs["package"], str):
                package_name = kwargs["package"]
            elif isinstance(kwargs["package"], TaskPackage):
                package_name = kwargs["package"].package_name
            else:
                raise TypeError("package填写错误")

            task_package = task_registry.task(package_name)
            if task_package:
                task_package.register(task)
        return task

    @classmethod
    def create_task_package_class(cls, package_name, **kwargs):
        # 将执行函数的参数和装饰器的参数合并到一块
        return type(package_name, (cls.base_package_class,), kwargs)

    @classmethod
    def create_task_package(cls, package_name, backend, *args, **kwargs):
        task_id = package_name
        task_package_cls = cls.create_task_class(package_name, **kwargs)
        task_package = task_package_cls(task_id, backend, *args, **kwargs)
        task_registry.register(task_package)
        return task_package

    @classmethod
    async def execute_task(cls, pool, task_id, *args, **kwargs):
        task = task_registry.task(task_id)
        if not task:
            print("task is None, stop running...")
            return

        print("开始处理任务 task: %s, args: %s, kwargs: %s" % (task, args, kwargs))
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

    def _execute(self, *args, **kwargs):
        try:
            result = self.do_exec_func(*args, **kwargs)
            print("任务执行成功, %s" % result)
            return True, result
        except Exception as e:
            error = e.args[0]
            return False, error

    def execute(self, *args, **kwargs):
        print("任务开始执行 task: %s, args: %s, kwargs: %s" % (self.task, args, kwargs))
        retry_num = self.task.retry
        result = None
        
        if retry_num:
            while retry_num:
                success, result = self._execute(*args, **kwargs)
                if success:
                    self.do_exec_success(result)
                    return result
                retry_num -= 1
        else:
            success, result = self._execute(*args, **kwargs)
            if success:
                self.do_exec_success(result)
                return result

        # 记录到数据库中
        if self.task.retry:
            self.do_exec_retry(result)
        else:
            self.do_exec_fail(result)
        return None

    def do_exec_func(self, *args, **kwargs):
        self.task.status = TaskStatusEnum.PROCESS.value
        self.result = self.task.execute(*args, **kwargs)
        return self.result

    # todo: 思考如何将任务的结果将task_id替换成随机的ID,而不是任务名字，否则无法重复执行
    def do_exec_success(self, return_value):
        self.task.status = TaskStatusEnum.SUCCESS.value
        self.task.backend.mark_task_success(task_id=self.task.task_id, result=return_value)

    def do_exec_fail(self, return_value):
        self.task.status = TaskStatusEnum.FAIL.value
        self.task.backend.mark_task_fail(task_id=self.task.task_id, result=return_value)

    def do_exec_retry(self, return_value):
        self.task.status = TaskStatusEnum.RETRY.value
        self.task.backend.mark_task_retry(task_id=self.task.task_id, result=return_value)


class TaskPackageTrace(object):
    """
    一个task对应一个trace
    """
    package = None
    result = None

    def __init__(self, package=None):
        self.package = package

    def _execute(self, *args):
        idx = 0
        result = None
        while idx < len(self.package.task_list):
            task = self.package.task_list[idx]
            # 有些任务并不需要参数，因此填空
            sub_args = args[idx] if idx < len(args) else ()
            try:
                result = self.do_exec_func(task, *sub_args)
                print("任务[%s]执行成功, 结果为[%s]" % (task, result))
                idx += 1
                continue
            except Exception as e:
                error = e.args[0]
                return False, error

        return True, result

    def execute(self, *args):
        print("任务包开始执行 task: %s, args: %s" % (self.package, args))
        retry_num = self.package.retry
        result = None

        if retry_num:
            while retry_num:
                success, result = self._execute(*args)
                if success:
                    self.do_exec_success(result)
                    return result
                retry_num -= 1
        else:
            success, result = self._execute(*args)
            if success:
                self.do_exec_success(result)
                return result

        # 记录到数据库中
        if self.package.retry:
            self.do_exec_retry(result)
        else:
            self.do_exec_fail(result)
        return None

    def do_exec_func(self, task, *args):
        self.package.status = TaskStatusEnum.PROCESS.value
        self.result = task.execute(*args)
        return self.result

    # todo: 思考如何将package的结果存储起来
    def do_exec_success(self, return_value):
        self.package.status = TaskStatusEnum.SUCCESS.value
        self.package.backend.mark_task_success(task_id=self.package.package_name, result=return_value)

    def do_exec_fail(self, return_value):
        self.package.status = TaskStatusEnum.FAIL.value
        self.package.backend.mark_task_fail(task_id=self.package.package_name, result=return_value)

    def do_exec_retry(self, return_value):
        self.package.status = TaskStatusEnum.RETRY.value
        self.package.backend.mark_task_retry(task_id=self.package.package_name, result=return_value)


def task_trace_execute(task, *args, **kwargs):
    return TaskTrace(task=task).execute(*args, **kwargs)


def package_trace_execute(package, *args):
    return TaskPackageTrace(package=package).execute(*args)
