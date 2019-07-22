#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-19
@file:      pool.py
@contact:   georgewang1994@163.com
@desc:      采用多进程、协程池
"""

import functools
import logging
from multiprocessing import cpu_count
from multiprocessing.pool import Pool
from queue import Queue

logger = logging.getLogger(__name__)


class ProcessPool(object):
    """
    进程池
    """
    def __init__(self, worker_count):
        self.queue = Queue()
        cpu_cnt = cpu_count()
        if not worker_count or worker_count > cpu_cnt:
            worker_count = cpu_cnt
        self.worker_count = worker_count

    def start(self):
        self.pool = Pool(processes=self.worker_count)

    def stop(self):
        self.pool.close()
        self.pool.join()

    def on_receive(self, success_callback, error_callback, result):
        is_success, result_value = result
        print("ProcessPool: 回调结果为 success: [%s], return value: [%s]" % (is_success, result_value))

        if is_success and success_callback:
            success_callback(result_value)

        if not is_success and error_callback:
            error_callback(result_value)

    def apply_async(self, executor_func, success_callback=None, error_callback=None, *args, **kwargs):
        print("ProcessPool: 丢进进程池中执行, executor_func: [%s]" % executor_func)
        callback = functools.partial(self.on_receive, success_callback, error_callback)
        self.pool.apply_async(func=executor_func, args=args, kwds=kwargs, callback=callback)
