#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-25
@file:      listener.py
@contact:   georgewang1994@163.com
@desc:      ...
"""
import time
from queue import Empty
from threading import Thread
from ammonia.base.task import TaskManager


class TaskListener(Thread):
    """
    负责监听consumer，将consumer中的消息给取出来
    """
    def __init__(self, task_consumer, ready_queue, *args, **kwargs):
        super(TaskListener, self).__init__(name="task_listener", target=self.consume, *args, **kwargs)
        self.task_consumer = task_consumer
        self.ready_queue = ready_queue

    def consume(self):
        """
        消费消息
        :return:
        """
        while True:
            task_msg = self.task_consumer.qos()
            if task_msg:
                self.ready_queue.put(task_msg)
            else:
                time.sleep(1)


class TaskQueueListener(Thread):
    """
    负责监听ready_queue，将队列中的消息给取出来，加入到协程池
    """
    def __init__(self, ready_queue, process_callback, *args, **kwargs):
        super(TaskQueueListener, self).__init__(name="task_queue_listener", target=self.consume, *args, **kwargs)
        self.ready_queue = ready_queue
        self.process_callback = process_callback

    def consume(self):
        """
        消费消息
        :return:
        """
        while True:
            try:
                task_msg = self.ready_queue.get(timeout=1)
                if task_msg:
                    task_manager = TaskManager.to_task(task_msg)
                    self.process_callback(task_manager)
                    self.ready_queue.task_done()
            except Empty:
                pass
