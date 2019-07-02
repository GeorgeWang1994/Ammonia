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
from ammonia.app import Ammonia
from ammonia.tests.test_base import TestDBBackendBase


ammonia = Ammonia()


@ammonia.task(routing_key=settings.LOW_TASK_ROUTING_KEY)
def get_sum(a, b):
    return a + b


class TestTask(TestDBBackendBase):
    def setUp(self):
        super().setUp()

    def test_basic_task_param(self):
        """
        测试基础的任务的参数的获取
        :return:
        """
        # 直接调用
        result = get_sum(1, 2)
        self.assertEqual(result, 3)
