#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-11
@file:      test_backends.py
@contact:   georgewang1994@163.com
@desc:      测试数据库连接
"""

from unittest import TestCase

from ammonia.backends.backend import DbBackend, RedisBackend
from ammonia.backends.models import TaskStatusEnum
from ammonia.settings import TEST_CASE_BACKEND_URL
from ammonia.tests.test_base import TestDBBackendBase
from ammonia.utils import generate_random_uid


class TestDbBackend(TestDBBackendBase):
    """
    测试数据库持久化
    """
    def setUp(self):
        super(TestDbBackend, self).setUp()
        self.backend = DbBackend(TEST_CASE_BACKEND_URL)

    def test_insert_update_get_task(self):
        """
        测试插入更新任务
        """
        task_id1 = generate_random_uid()
        self.backend.mark_task_success(task_id=task_id1, result=100)
        result = self.backend.get_task(task_id1)
        self.assertEqual(result.status, TaskStatusEnum.SUCCESS.value)
        self.assertEqual(result.result, 100)

        task_id2 = generate_random_uid()
        self.backend.mark_task_fail(task_id=task_id2, result={"error": "error"})
        result = self.backend.get_task(task_id2)
        self.assertEqual(result.status, TaskStatusEnum.FAIL.value)
        self.assertEqual(result.traceback, {"error": "error"})


class TestRedisBackend(TestCase):
    """
    测试Redis持久化
    """
    def setUp(self):
        url = "redis://@localhost:6379/0"
        self.backend = RedisBackend(url)

    def test_mark_and_get_task(self):
        task_id1 = generate_random_uid()
        self.backend.mark_task_success(task_id=task_id1, result=3)
        result = self.backend.get_task_result(task_id1)
        self.assertEqual(result, 3)
