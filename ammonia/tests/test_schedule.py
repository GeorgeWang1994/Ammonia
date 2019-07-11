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

from ammonia.tests.test_base import ammonia, TestDBBackendBase
from ammonia.worker.schedule import Schedule


@ammonia.task(eta=datetime.datetime.now())
def get_sum(a, b):
    return a + b


@ammonia.task(wait=datetime.timedelta(seconds=1))
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
        get_sum(1, 2)
        self.assertIsNotNone(get_sum.start_time)
        start_time = datetime.datetime.now()
        # 为了方便计算，重新对任务的开始时间进行了赋值
        get_sum.start_time = start_time
        self.schedule.time_task_list.append(get_sum)
        result, next_internal_time = self.schedule.get_need_execute_tasks(
            start_time - datetime.timedelta(seconds=0.5)
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].task_name, get_sum.task_name)
        self.assertEqual(next_internal_time, 1000)

        result, next_internal_time = self.schedule.get_need_execute_tasks(
            start_time + datetime.timedelta(seconds=0.5)
        )
        self.assertEqual(len(result), 0)
        self.assertEqual(next_internal_time, 1000)

    def test_schedule_for_wait(self):
        get_sum2(1, 2)  # start_time成功计算赋值，设置为当前时间后的一秒
        self.assertIsNotNone(get_sum2.start_time)

        start_time = datetime.datetime.now()
        self.schedule.time_task_list.append(get_sum2)
        result, next_internal_time = self.schedule.get_need_execute_tasks(start_time)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].task_name, get_sum2.task_name)
        self.assertEqual(next_internal_time, 1000)

        result, next_internal_time = self.schedule.get_need_execute_tasks(
            start_time + datetime.timedelta(seconds=1)
        )
        self.assertEqual(len(result), 0)
        self.assertEqual(next_internal_time, 1000)
