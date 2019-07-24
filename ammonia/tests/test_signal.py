#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-07-23
@file:      test_signal.py
@contact:   georgewang1994@163.com
@desc:      测试信号机制
"""

from ammonia.signals import task_retry, task_process, task_success, task_prepare, task_fail
from ammonia.state import TaskStatusEnum
from ammonia.tests import TestDBBackendBase, ammonia
from ammonia.utils.signal import receiver

result = {
    "retry": False,
    "process": False,
    "prepare": False,
    "success": False,
    "fail": False,
}


def init_status():
    global result
    result = {item.value: False for item in TaskStatusEnum}


@ammonia.task(retry=3)
def test_task_retry_func(a, b):
    return a + b


@receiver(signals=[task_retry], sender=test_task_retry_func.task.task_name)
def process_task_retry_data(sender, task_id, task_name, exec_args, exe_kwargs, *args, **kwargs):
    result["retry"] = True


@receiver(signals=[task_process], sender=test_task_retry_func.task.task_name)
def process_task_process_data(sender, task_id, task_name, exec_args, exe_kwargs, *args, **kwargs):
    result["process"] = True


@receiver(signals=[task_prepare], sender=test_task_retry_func.task.task_name)
def process_task_prepare_data(sender, task_id, task_name, exec_args, exe_kwargs, *args, **kwargs):
    result["prepare"] = True


@receiver(signals=[task_success], sender=test_task_retry_func.task.task_name)
def process_task_success_data(sender, task_id, task_name, exec_args, exe_kwargs, *args, **kwargs):
    result["success"] = True


@receiver(signals=[task_fail], sender=test_task_retry_func)
def process_task_fail_data(sender, task_id, task_name, exec_args, exe_kwargs, *args, **kwargs):
    result["fail"] = True


class TestSignal(TestDBBackendBase):

    def test_task_related(self):
        init_status()
        res = test_task_retry_func(1, 2)
        self.assertEqual(res.get(), 3)
        self.assertTrue(result["prepare"])
        self.assertTrue(result["process"])
        self.assertTrue(result["success"])

        self.assertFalse(result["fail"])
        self.assertFalse(result["retry"])

        init_status()
        res = test_task_retry_func(1, '2')
        self.assertTrue(result["prepare"])
        self.assertTrue(result["process"])
        self.assertTrue(result["retry"])

        self.assertFalse(result["fail"])
        self.assertFalse(result["success"])
