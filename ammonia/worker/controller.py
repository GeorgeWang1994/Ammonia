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
from ammonia.worker.pool import ProcessPool
from ammonia.worker.schedule import Schedule


class WorkerController(object):
    """
    控制worker
    """
    def __init__(self, pool_worker_count=10):
        self.ready_queue = Queue()
        self.schedule = Schedule(ready_queue=self.ready_queue)
        self.pool = ProcessPool(worker_count=pool_worker_count)
        self.queue_listener = TaskQueueListener(ready_queue=self.ready_queue, pool=self.pool)
        self.listener = TaskListener(ready_queue=self.ready_queue, schedule=self.schedule)
        # 保证listener在最后面运行，在主线程阻塞获取消息
        self.workers = (
            self.queue_listener,
            self.schedule,
            self.pool,
            self.listener,
        )

    def start(self):
        for worker in self.workers:
            worker.start()

    def stop(self):
        for worker in reversed(self.workers):
            worker.stop()
