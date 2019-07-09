#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-06-08
@file:      test_task.py
@contact:   georgewang1994@163.com
@desc:      测试任务
"""

from ammonia import settings
from ammonia.base.registry import task_registry
from ammonia.state import TaskStatusEnum
from ammonia.tests.test_base import TestDBBackendBase, ammonia


@ammonia.task(routing_key=settings.LOW_TASK_ROUTING_KEY)
def test_basic_task_param_func(a, b):
    return a + b


@ammonia.task(retry=3)
def test_task_retry_func(a, b):
    return a + b


package1 = ammonia.create_package("test_create_package", dependent=True)


@ammonia.task(package=package1)
def test_task_package_task1(a, b):
    return a + 2, b + 3


@ammonia.task(package=package1)
def test_task_package_task2(a, b):
    return a * b


class TestTask(TestDBBackendBase):
    def setUp(self):
        super().setUp()

    def test_basic_task_param(self):
        """
        测试基础的任务的参数的获取
        :return:
        """
        # 直接调用
        result = test_basic_task_param_func(1, 2)
        self.assertEqual(result, 3)

        task = task_registry.get('test_task.test_basic_task_param_func')
        self.assertEqual(task.status, TaskStatusEnum.SUCCESS.value)

    def test_task_try(self):
        """
        测试任务重试
        :return:
        """
        result = test_task_retry_func(1, "2")
        self.assertEqual(result, None)

        task = task_registry.get('test_task.test_task_retry_func')
        self.assertEqual(task.status, TaskStatusEnum.RETRY.value)

    def test_task_package(self):
        """
        测试任务包
        :return:
        """
        result = package1((1, 2))  # (1 + 2) * (2 + 3)
        self.assertEqual(result, 15)

        task = task_registry.get('test_create_package')
        self.assertEqual(task.status, TaskStatusEnum.SUCCESS.value)
