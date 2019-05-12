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
from ammonia.backends.models import BASE, TaskStatusChoice, Task
from ammonia.utils import generate_random_uid


class TestBase(unittest.TestCase):
    def setUp(self):
        # 创建表
        self.backend = DbBackend('mysql+pymysql://root:123456@localhost/ammonia?charset=utf8', encoding='utf-8')
        BASE.metadata.create_all(self.backend.engine)

    def tearDown(self):
        # 将表删除
        self.backend.session.query(Task).filter().delete()
        self.backend.session.commit()


class TestDbBackend(TestBase):
    """
    测试数据持久化
    """
    def test_insert_delete_get_task(self):
        """
        测试插入删除获取任务
        """
        task_id1 = generate_random_uid()
        self.backend.insert_task(task_id1)
        task_id2 = generate_random_uid()
        self.backend.insert_task(task_id2, TaskStatusChoice.PROCESSING)
        task_id3 = generate_random_uid()
        self.backend.insert_task(task_id3, TaskStatusChoice.FINISH, "3", {"error": "type error"})

        result = self.backend.get_task(task_id1)
        self.assertEqual(result.task_id, task_id1)
        self.assertEqual(result.status, TaskStatusChoice.START)

        result = self.backend.get_tasks_by_status(TaskStatusChoice.PROCESSING)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].task_id, task_id2)

        result = self.backend.get_error_tasks()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].task_id, task_id3)

