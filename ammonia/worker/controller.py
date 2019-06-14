#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-24
@file:      controller.py
@contact:   georgewang1994@163.com
@desc:      控制worker
"""

from queue import Queue

from ammonia.base.task import TaskManager
from ammonia.worker.listener import TaskListener, TaskQueueListener
from ammonia.worker.pool import AsyncPool


class WorkerController(object):
    """
    控制worker
    """
    def __init__(self, pool_worker_count=10):
        self.ready_queue = Queue()
        self.listener = TaskListener(ready_queue=self.ready_queue)
        self.queue_listener = TaskQueueListener(ready_queue=self.ready_queue, process_callback=self.process_task)
        self.pool = AsyncPool(pool_worker_count)
        self.workers = (
            self.listener,
            self.queue_listener,
            self.pool,
        )

    def process_task(self, task):
        TaskManager.execute_task(self.pool, task)

    def start(self):
        """
        :return:
        """
        for worker in self.workers:
            worker.start()
