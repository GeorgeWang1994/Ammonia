#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-06-08
@file:      test_task.py
@contact:   georgewang1994@163.com
@desc:      测试任务
"""

import datetime

from ammonia import settings
from ammonia.state import TaskStatusEnum
from ammonia.tests.test_base import TestDBBackendBase, ammonia


@ammonia.task(routing_key=settings.LOW_TASK_ROUTING_KEY)
def test_basic_task_param_func(a, b):
    return a + b


@ammonia.task(retry=3)
def test_task_retry_func(a, b):
    return a + b


package1 = ammonia.create_package("test_create_package", dependent=True, routing_key="abc")


@ammonia.task(package=package1)
def test_task_package_task1(a, b):
    return a + 2, b + 3


@ammonia.task(package=package1, routing_key="abc")
def test_task_package_task2(a, b):
    return a * b


@ammonia.task(eta=datetime.datetime.now(), wait=datetime.timedelta(seconds=10))
def test_task_eta_or_wait(a, b):
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
        self.assertEqual(test_basic_task_param_func.status, TaskStatusEnum.SUCCESS.value)

    def test_task_try(self):
        """
        测试任务重试
        :return:
        """
        result = test_task_retry_func(1, "2")
        self.assertEqual(result, None)
        self.assertEqual(test_task_retry_func.status, TaskStatusEnum.RETRY.value)

    def test_task_package(self):
        """
        测试任务包
        :return:
        """
        result = package1((1, 2))  # (1 + 2) * (2 + 3)
        self.assertTrue(package1.is_package)
        self.assertEqual(package1.routing_key, "abc")
        self.assertEqual(result, 15)
        self.assertEqual(package1.status, TaskStatusEnum.SUCCESS.value)

    def test_task_eta_and_wait(self):
        """
        测试任务eta和wait参数
        :return:
        """
        result = test_task_eta_or_wait(1, 2)
        self.assertEqual(test_task_eta_or_wait.status, TaskStatusEnum.SUCCESS.value)
        self.assertTrue(isinstance(test_task_eta_or_wait.task.eta, float))
        self.assertTrue(isinstance(test_task_eta_or_wait.task.wait, float))
        self.assertEqual(result, 2)
