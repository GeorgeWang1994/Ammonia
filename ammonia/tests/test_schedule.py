#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-07-11
@file:      test_schedule.py
@contact:   georgewang1994@163.com
@desc:      测试schedule
"""
import datetime
from queue import Queue

from freezegun import freeze_time

from ammonia.tests.test_base import ammonia, TestDBBackendBase
from ammonia.worker.schedule import Schedule


@ammonia.task(eta=datetime.datetime.now() + datetime.timedelta(seconds=1))
def get_sum(a, b):
    return a + b


@ammonia.task(wait=datetime.timedelta(seconds=0.5))
def get_sum2(a, b):
    return a + b


class TestSchedule(TestDBBackendBase):
    """
    测试定时任务
    """
    def setUp(self):
        self.ready_queue = Queue()
        self.schedule = Schedule(ready_queue=self.ready_queue)
        super(TestSchedule, self).setUp()

    def test_schedule_for_eta(self):
        start_time = datetime.datetime.now()
        with freeze_time(start_time):
            result = get_sum(1, 2)
            self.assertIsNotNone(get_sum.start_time)
            self.assertEqual(result.get(), 3)
            # 为了方便计算，重新对任务的开始时间进行了赋值
            self.schedule.register_task(get_sum.data)
            result, next_internal_time = self.schedule.get_need_execute_task(start_time.timestamp())
            self.assertEqual(result["task_id"], get_sum.task_id)
            self.assertIsNone(next_internal_time)

            result, next_internal_time = self.schedule.get_need_execute_task(
                start_time.timestamp() + 1
            )
            self.assertIsNone(result)
            self.assertIsNone(next_internal_time)

    def test_schedule_for_wait(self):
        start_time = datetime.datetime.now()
        with freeze_time(start_time):
            result = get_sum2(1, 2)
            self.assertIsNotNone(get_sum2.start_time)
            self.assertEqual(result.get(), 3)
            # 为了方便计算，重新对任务的开始时间进行了赋值
            self.schedule.register_task(get_sum2.data)
            result, next_internal_time = self.schedule.get_need_execute_task(start_time.timestamp())
            self.assertEqual(result["task_id"], get_sum2.task_id)
            self.assertIsNone(next_internal_time)

            result, next_internal_time = self.schedule.get_need_execute_task(
                start_time.timestamp() + 1
            )
            self.assertIsNone(result)
            self.assertIsNone(next_internal_time)
