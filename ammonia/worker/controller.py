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

from ammonia.worker.listener import TaskListener, TaskQueueListener
from ammonia.mq import TaskConsumer, TaskProducer
from ammonia.worker.pool import AsyncPool


class WorkerController(object):
    """
    控制worker
    """
    def __init__(self, pool_worker_count=10):
        self.task_consumer = TaskConsumer()
        self.task_producer = TaskProducer()
        self.ready_queue = Queue()
        self.listener = TaskListener(task_consumer=self.task_consumer, ready_queue=self.ready_queue)
        self.queue_listener = TaskQueueListener(ready_queue=self.ready_queue, process_callback=self.process_task)
        self.pool = AsyncPool(pool_worker_count)
        self.workers = (
            self.listener,
            self.queue_listener,
            self.pool,
        )

    def process_task(self, task_manager):
        self.pool.apply_async(task_manager.task.exec_func())

    def start(self):
        """
        :return:
        """
        for worker in self.workers:
            worker.start()
