#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-20
@file:      test_pool.py
@contact:   georgewang1994@163.com
@desc:      测试协程池、进程池
"""

from ammonia.backends.backend import DbBackend
from ammonia.base.task import TaskManager
from ammonia.settings import TEST_CASE_BACKEND_URL
from ammonia.tests.test_base import ammonia, TestDBBackendBase
from ammonia.worker.pool import ProcessPool


@ammonia.task()
def get_sum(a, b):
    return a + b


class TestSchedule(TestDBBackendBase):
    """
    测试定时任务
    """
    def setUp(self):
        super(TestSchedule, self).setUp()
        self.pool = ProcessPool(worker_count=4)
        self.pool.start()
        self.backend = DbBackend(TEST_CASE_BACKEND_URL)

    def test_pool(self):
        # 设置执行的参数
        get_sum.base_process_task(1, 2)

        exe_result = TaskManager.execute_task(self.pool, get_sum.data)
        self.assertEqual(exe_result, (True, 3))

        result = self.backend.get_task_result(get_sum.task_id)
        self.assertEqual(result, (True, 3))
