#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-11
@file:      test_backends.py
@contact:   georgewang1994@163.com
@desc:      测试数据库连接
"""

import unittest

from ammonia.backends.database import DbBackend


class TestDbBackend(unittest.TestCase):
    """
    测试数据持久化
    """
    def setUp(self):
        self.backend = DbBackend('mysql+mysqldb://root:8080@localhost/ammonia_backend', encoding='utf-8')

    def test_insert_delete_task(self):
        """
        测试插入删除任务
        """
        pass

    def test_get_task(self):
        """
        测试获取任务信息
        """
        pass
