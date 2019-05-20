#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-19
@file:      test_serializer.py
@contact:   georgewang1994@163.com
@desc:      测试序列化
"""
from unittest import TestCase

from ammonia.serializer import Serializer


class TestSerializer(TestCase):
    """
    测试序列化模块
    """
    def setUp(self):
        self.data = {"first": 1, "second": 2}

    def test_serializer(self):
        modules = ['pickle']
        for module in modules:
            serializer = Serializer(default_module=module)
            result = serializer.loads(serializer.dumps(self.data))
            self.assertDictEqual(result, self.data)
