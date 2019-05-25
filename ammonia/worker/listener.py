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
from queue import Queue
from threading import Thread


class TaskListener(Thread):
    """
    负责监听consumer，将consumer中的消息给取出来
    """
    def __init__(self, task_consumer, *args, **kwargs):
        super(TaskListener, self).__init__(name="task_listener", target=self.consume, *args, **kwargs)
        self.ready_queue = Queue()
        self.task_consumer = task_consumer

    def consume(self):
        """
        消费消息
        :return:
        """
        while True:
            task_msg = self.task_consumer.qos()
            if not task_msg:
                self.ready_queue.put(task_msg)
            else:
                time.sleep(1)
