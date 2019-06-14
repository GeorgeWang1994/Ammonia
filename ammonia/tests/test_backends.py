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

from ammonia.backends.backend import DbBackend
from ammonia.backends.models import TaskStatusEnum, Task
from ammonia.utils import generate_random_uid


class TestBase(unittest.TestCase):
    def setUp(self):
        # 创建表
        self.backend = DbBackend('mysql+pymysql://root:123456@localhost/ammonia?charset=utf8')

    def tearDown(self):
        # 将表删除
        self.backend.session.query(Task).filter().delete()
        self.backend.session.commit()


class TestDbBackend(TestBase):
    """
    测试数据持久化
    """
    def test_insert_update_get_task(self):
        """
        测试插入更新任务
        """
        task_id1 = generate_random_uid()
        self.backend.mark_task_success(task_id=task_id1, result=100)
        result = self.backend.get_task(task_id1)
        self.assertEqual(result.status, TaskStatusEnum.SUCCESS.value)

        task_id2 = generate_random_uid()
        self.backend.mark_task_fail(task_id=task_id2, result={"error": "error"})
        result = self.backend.get_task(task_id2)
        self.assertEqual(result.status, TaskStatusEnum.FAIL.value)
