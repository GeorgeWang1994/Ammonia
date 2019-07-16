#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-24
@file:      controller.py
@contact:   georgewang1994@163.com
@desc:      控制worker
"""

import asyncio
from queue import Queue

from ammonia.base.task import TaskManager
from ammonia.worker.listener import TaskListener, TaskQueueListener
from ammonia.worker.pool import AsyncPool
from ammonia.worker.schedule import Schedule


class WorkerController(object):
    """
    控制worker
    """

    def __init__(self, pool_worker_count=10):
        self.ready_queue = Queue()
        self.loop = asyncio.get_event_loop()
        self.schedule = Schedule(ready_queue=self.ready_queue)
        self.pool = AsyncPool(pool_worker_count, self.loop)
        self.queue_listener = TaskQueueListener(ready_queue=self.ready_queue,
                                                process_callback=self.process_task, loop=self.loop)
        self.listener = TaskListener(ready_queue=self.ready_queue, schedule=self.schedule)
        self.workers = (
            self.queue_listener,
            self.schedule,
            self.pool,
            self.listener,
        )

    async def process_task(self, task):
        await TaskManager.execute_task(self.pool, task)

    def start(self):
        """
        :return:
        """
        try:
            for worker in self.workers:
                worker.start()
        finally:
            self.close()

    def close(self):
        for worker in reversed(self.workers):
            if isinstance(worker, AsyncPool):
                # 等待stop函数完成
                loop = asyncio.get_event_loop()
                loop.run_until_complete(worker.stop())
            else:
                worker.stop()
