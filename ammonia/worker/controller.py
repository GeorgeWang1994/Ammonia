#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-24
@file:      controller.py
@contact:   georgewang1994@163.com
@desc:      控制worker
"""

from ammonia.worker.listener import TaskListener
from ammonia.worker.mq import TaskConsumer, TaskProducer


class WorkerController(object):
    """
    控制worker
    """
    def __init__(self):
        self.task_consumer = TaskConsumer()
        self.task_producer = TaskProducer()
        self.listener = TaskListener(task_consumer=self.task_consumer)

        self.workers = (
            self.listener,
        )

    def init(self):
        self.task_consumer.register_callback({})

    def process_task(self):
        pass

    def start(self):
        """
        :return:
        """
        self.init()
        for worker in self.workers:
            worker.start()
