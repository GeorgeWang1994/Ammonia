#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-06-08
@file:      test_task.py
@contact:   georgewang1994@163.com
@desc:      测试任务
"""

from unittest import TestCase

from ammonia.ammonia import Ammonia


class TestTask(TestCase):
    def setUp(self):
        pass

    def test_basic_task_param(self):
        """
        测试基础的任务的参数的获取
        :return:
        """
        @Ammonia.task(routing_key="task1")
        def get_sum(a, b):
            return a + b

        result = get_sum.defer(1, 2)
        result = result.get()
        self.assertEqual(result, 3)
