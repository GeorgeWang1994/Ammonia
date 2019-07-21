#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-24
@file:      task.py
@contact:   georgewang1994@163.com
@desc:      任务相关的类
"""

import datetime
import sys
from collections import Iterable

from ammonia.backends.backend import get_backend_by_settings
from ammonia.base.registry import task_registry
from ammonia.base.result import AsyncResult
from ammonia.mq import TaskProducer, TaskConnection, task_exchange, task_queues
from ammonia.state import TaskStatusEnum
from ammonia.utils import generate_random_routing_key
from ammonia.utils import generate_random_uid


class Crontab(object):
    def __init__(self, month="*", day="*", hour="*", minute="*", second="*"):
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second

    @property
    def data(self):
        return {
            "month": self.month,
            "day": self.day,
            "hour": self.hour,
            "minute": self.minute,
            "second": self.second,
        }


class BaseTask(object):
    """
    基础任务
    """
    def __init__(self, task_name, **kwargs):
        # 这里的args和kwargs是函数的，而装饰器的参数则是类的参数
        self.task_name = task_name
        self.routing_key = getattr(self, "routing_key", generate_random_routing_key())
        self.retry = getattr(self, "retry", 0)
        self.crontab = getattr(self, "crontab", None)

        self.eta = getattr(self, "eta", None)  # 具体的执行时间，格式为datetime
        if self.eta:
            if not isinstance(self.eta, datetime.datetime):
                raise TypeError("eta类型错误，应该是datetime.datetime类型")
            self.eta = self.eta.timestamp()

        self.wait = getattr(self, "wait", None)
        if self.wait:
            if not isinstance(self.wait, datetime.timedelta):
                raise TypeError("wait类型错误，应该是datetime.timedelta类型")
            self.wait = self.wait.total_seconds()  # 等待执行的时间间隔，格式为delta

    def execute(self):
        raise NotImplementedError

    @property
    def data(self):
        data = {
            "task_name": self.task_name,
            "routing_key": self.routing_key,
            "retry": self.retry,
        }
        if self.wait:
            data.update({"wait": self.wait})
        if self.eta:
            data.update({"eta": self.eta})
        if self.crontab:
            data.update({"crontab": self.crontab.data})
        return data


class ExecuteBaseTask(object):
    """
    执行任务
    """
    def __init__(self, task_name, **kwargs):
        self.task_id = kwargs.get("task_id", None)
        self.task = task_registry[task_name]
        self.status = kwargs.get("status", TaskStatusEnum.CREATED.value)
        self.start_time = kwargs.get("start_time", None)
        self.execute_args = kwargs.get("execute_args", ())  # 执行函数的参数
        self.execute_kwargs = kwargs.get("execute_kwargs", {})  # 执行函数的参数
        self.is_package = kwargs.get("is_package", False)
        from ammonia.app import Ammonia
        backend_cls = get_backend_by_settings(Ammonia.conf["BACKEND_TYPE"])
        self.backend = backend_cls(Ammonia.conf["BACKEND_URL"])

    def __str__(self):
        raise NotImplementedError

    @classmethod
    def get_task_producer(cls, channel, routing_key=None):
        return TaskProducer(channel=channel, routing_key=routing_key, exchange=task_exchange, serializer='json')

    @property
    def data(self):
        raise NotImplementedError

    def defer_async(self):
        """
        这里的参数是执行函数的参数，延迟执行
        :return:
        """
        from ammonia.app import Ammonia
        with TaskConnection(hostname=Ammonia.conf["TASK_URL"],
                            connect_timeout=Ammonia.conf["TASK_CONNECTION_TIMEOUT"]) as conn:
            routing_key = self.task.routing_key
            print("发送消息给路由%s %s" % (routing_key, self.data))
            producer = self.get_task_producer(channel=conn, routing_key=routing_key)
            producer.publish_task(self.data, routing_key=routing_key,
                                  exchange=task_exchange, declare=task_queues)

    @property
    def execute_time(self):
        return self.start_time

    def __call__(self, *args, **kwargs):
        self.base_process_task(*args, **kwargs)
        return self.process_task(True, *args, **kwargs)

    def defer(self, *args, **kwargs):
        self.base_process_task(*args, **kwargs)
        return self.process_task(False, *args, **kwargs)

    def process_task(self, is_immediate=False, *args, **kwargs):
        raise NotImplemented

    def base_process_task(self, *args, **kwargs):
        self.start_time = datetime.datetime.now().timestamp()
        if self.task.eta:
            self.start_time = self.task.eta
        elif self.task.wait:
            self.start_time = self.start_time + self.task.wait

        # 每次重新执行都会替换掉task_id
        self.task_id = generate_random_uid()
        self.execute_args = args
        self.execute_kwargs = kwargs
        self.status = TaskStatusEnum.PREPARE.value


class Task(ExecuteBaseTask):

    def __str__(self):
        return "task[%s-%s]" % (self.task_id, self.status)

    @property
    def data(self):
        data = self.task.data
        data.update({
            "task_id": self.task_id, "status": self.status, "is_package": self.is_package,
            "execute_args": self.execute_args, "execute_kwargs": self.execute_kwargs,
        })

        if self.start_time:
            data.update({"start_time": self.start_time})
        return data

    def execute(self, *args, **kwargs):
        return self.task.execute(*args, **kwargs)

    def process_task(self, is_immediate=False, *args, **kwargs):
        """
        :param is_immediate: 是否立即执行
        :return:
        """
        # 如果是直接调用，则直接计算返回
        if is_immediate:
            task_trace_execute(self.data)
        else:
            self.defer_async()
        return AsyncResult(task_id=self.task_id, backend=self.backend)


class TaskPackage(ExecuteBaseTask):
    """
    将task都封装到package中，用于执行一系列任务
    """
    def __init__(self, task_name, **kwargs):
        super(TaskPackage, self).__init__(task_name, **kwargs)
        self.task_name = task_name
        self.is_dependent = kwargs.get("dependent", False)  # 是否前一个任务依赖于上一个任务的结果
        self.routing_key = kwargs.get("routing_key", generate_random_routing_key())
        self.task_list = self.init_task_list(kwargs.get("task_list", []))
        self.retry = getattr(self, "retry", 0)
        self.crontab = getattr(self, "crontab", None)

        self.eta = getattr(self, "eta", None)  # 具体的执行时间，格式为datetime
        if self.eta:
            if not isinstance(self.eta, datetime.datetime):
                raise TypeError("eta类型错误，应该是datetime.datetime类型")
            self.eta = self.eta.timestamp()

        self.wait = getattr(self, "wait", None)
        if self.wait:
            if not isinstance(self.wait, datetime.timedelta):
                raise TypeError("wait类型错误，应该是datetime.timedelta类型")
            self.wait = self.wait.total_seconds()  # 等待执行的时间间隔，格式为delta
        self.is_package = True

    def __str__(self):
        return "package[%s-%s]" % (self.task_id, self.status)

    @classmethod
    def init_task_list(cls, task_info_list):
        return [TaskManager.create_exe_task_or_package(False, **task_info) for task_info in task_info_list]

    def register(self, exe_task):
        self.task_list.append(exe_task)

    @property
    def data(self):
        data = {
            "task_id": self.task_id, "status": self.status, "is_package": self.is_package,
            "execute_args": self.execute_args, "execute_kwargs": self.execute_kwargs,
            "task_list": [task.data for task in self.task_list], "dependent": self.is_dependent,
            "task_name": self.task_name, "routing_key": self.routing_key, "retry": self.retry,
        }

        if self.wait:
            data.update({"wait": self.wait})
        if self.eta:
            data.update({"eta": self.eta})
        if self.crontab:
            data.update({"crontab": self.crontab.data})
        if self.start_time:
            data.update({"start_time": self.start_time})
        return data

    def process_task(self, is_immediate=False, *args, **kwargs):
        """
        :param is_immediate: 是否立即执行
        :return:
        """
        if not self.task_list:
            raise Exception("任务包中的任务为空")

        if len(self.task_list) <= 1:
            raise Exception("任务包中任务个数至少为两个")

        # 如果是直接调用，则直接计算返回
        if is_immediate:
            task_trace_execute(self.data)
        else:
            self.defer_async()
        return AsyncResult(task_id=self.task_id, backend=self.backend)


class TaskManager(object):
    base_task_class = BaseTask
    base_exe_task_class = Task
    base_exe_package_class = TaskPackage

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
    def create_task(cls, execute_func, *args, **kwargs):
        task_module = sys.modules[execute_func.__module__]
        task_name = ".".join([task_module.__name__, execute_func.__name__, ])
        task_cls = cls.create_task_class(execute_func, **kwargs)
        base_task = task_cls(task_name, *args, **kwargs)
        task_registry.register(base_task)  # 注册基础任务

        exe_task = cls.base_exe_task_class(task_name=task_name)
        # 如果填写了package的话，需要注册到package
        if kwargs.get("package"):
            if isinstance(kwargs["package"], TaskPackage):
                package = kwargs["package"]
            else:
                raise TypeError("package填写错误")

            package.register(exe_task)

        # 创建执行任务
        return exe_task

    @classmethod
    def create_task_package_class(cls, package_name, **kwargs):
        task_settings = {
            'execute': None,
        }
        # 将执行函数的参数和装饰器的参数合并到一块
        task_settings.update(kwargs)

        return type(package_name, (cls.base_task_class,), task_settings)

    @classmethod
    def create_task_package(cls, package_name, *args, **kwargs):
        task_cls = cls.create_task_package_class(package_name, **kwargs)
        task = task_cls(package_name, *args, **kwargs)
        task_registry.register(task)  # 注册基础任务

        return cls.base_exe_package_class(package_name, **kwargs)

    @classmethod
    def create_exe_task_or_package(cls, need_check=True, **task_kwargs):
        """
        创建任务或者package
        :param need_check: 在任务package中不需要判断task_id
        :param task_kwargs:
        :return:
        """
        is_package = task_kwargs.get("is_package", False)
        task_name = task_kwargs.pop("task_name")
        if not task_name:
            raise KeyError("任务名字未找到")

        if need_check:
            task_id = task_kwargs.get("task_id")
            if not task_id:
                raise KeyError("任务id未找到")

        exe_cls = cls.base_exe_task_class
        if is_package:
            exe_cls = cls.base_exe_package_class
        return exe_cls(task_name, **task_kwargs)

    @classmethod
    def execute_task(cls, pool, task_kwargs):
        print("开始处理任务 task_kwargs: task_kwargs" % task_kwargs)
        return pool.apply_async(task_trace_execute, cls.on_task_success, cls.on_task_fail, task_kwargs)
        # todo: 将消息的消费放到执行任务的后面，保证消息在中间过程中因为不可抗原因而导致消失

    @classmethod
    def on_task_success(cls, return_value):
        print("任务执行成功，返回结果为%s" % return_value)

    @classmethod
    def on_task_fail(cls, return_value):
        print("任务执行失败，返回结果为%s" % return_value)


class BaseTrace(object):
    def __init__(self, task):
        self.task_id = task.task_id
        self.task_or_package = task
        self.result = None

    def _execute(self, *args, **kwargs):
        raise NotImplemented

    def execute(self, *args, **kwargs):
        print("任务开始执行 task: %s, args: %s, kwargs: %s" % (self.task_or_package, args, kwargs))
        retry_num = self.task_or_package.task.retry
        result = None

        tmp_retry_num = retry_num
        if tmp_retry_num:
            while tmp_retry_num:
                success, result = self._execute(*args, **kwargs)
                if success:
                    self.do_exec_success(result)
                    return True, result
                tmp_retry_num -= 1
        else:
            success, result = self._execute(*args, **kwargs)
            if success:
                self.do_exec_success(result)
                print("任务[%s]执行成功, 结果为[%s]" % (self.task_or_package, result))
                return True, result
            else:
                print("任务[%s]执行失败, 结果为[%s]" % (self.task_or_package, result))

        # 记录到数据库中
        if retry_num:
            self.do_exec_retry(result)
        else:
            self.do_exec_fail(result)
        return False, None

    def do_exec_func(self, *args, **kwargs):
        raise NotImplemented

    def do_exec_success(self, return_value):
        self.task_or_package.status = TaskStatusEnum.SUCCESS.value
        self.task_or_package.backend.mark_task_success(task_id=self.task_id, result=return_value)

    def do_exec_fail(self, return_value):
        self.task_or_package.status = TaskStatusEnum.FAIL.value
        self.task_or_package.backend.mark_task_fail(task_id=self.task_id, result=return_value)

    def do_exec_retry(self, return_value):
        self.task_or_package.status = TaskStatusEnum.RETRY.value
        self.task_or_package.backend.mark_task_retry(task_id=self.task_id, result=return_value)


class TaskTrace(BaseTrace):
    """
    一个task对应一个trace
    """
    def _execute(self, *args, **kwargs):
        try:
            result = self.do_exec_func(*args, **kwargs)
            return True, result
        except Exception as e:
            error = e.args[0]
            return False, error

    def do_exec_func(self, *args, **kwargs):
        self.task_or_package.status = TaskStatusEnum.PROCESS.value
        self.result = self.task_or_package.execute(*args, **kwargs)
        return self.result


class TaskPackageTrace(BaseTrace):
    """
    一个task对应一个trace
    """
    def _execute(self, *args):
        idx = 0
        last_result = None
        result = None
        while idx < len(self.task_or_package.task_list):
            task = self.task_or_package.task_list[idx]
            if not self.task_or_package.is_dependent:
                # 有些任务并不需要参数，因此填空
                sub_args = args[idx] if idx < len(args) else ()
            else:
                # 任务依赖遇上一个任务的结果作为参数
                if idx > 0:
                    sub_args = last_result if isinstance(last_result, Iterable) else (last_result,)
                else:
                    sub_args = args[0] if args else ()
            try:
                result = self.do_exec_func(task, *sub_args)
                last_result = result
                idx += 1
                continue
            except Exception as e:
                error = e.args[0]
                return False, error

        return True, result

    def do_exec_func(self, task, *args):
        self.task_or_package.status = TaskStatusEnum.PROCESS.value
        self.result = task.execute(*args)
        return self.result


def task_trace_execute(task_kwargs):
    exe_task = TaskManager.create_exe_task_or_package(**task_kwargs)

    if not exe_task.is_package:
        return TaskTrace(task=exe_task).execute(*exe_task.execute_args, **exe_task.execute_kwargs)

    return TaskPackageTrace(task=exe_task).execute(*exe_task.execute_args, **exe_task.execute_kwargs)
