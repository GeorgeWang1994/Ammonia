#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-25
@file:      listener.py
@contact:   georgewang1994@163.com
@desc:      ...
"""
import logging
import time
from queue import Empty
from threading import Thread

from ammonia.base.task import TaskManager, TaskConsumer
from ammonia.mq import TaskConnection, TaskExchange, TaskQueue
from ammonia.settings import TASK_ROUTING_KEY

logger = logging.getLogger(__name__)


class TaskListener(object):
    """
    负责监听consumer，将consumer中的消息给取出来
    """
    def __init__(self, ready_queue, *args, **kwargs):
        self.task_consumer = None
        self.ready_queue = ready_queue
        self._connection = None

    def establish_connection(self):
        if self.task_consumer:
            return

        self._connection = TaskConnection()
        self._connection.connect()
        exchange = TaskExchange(channel=self._connection.channel())
        queues = [TaskQueue(routing_key=TASK_ROUTING_KEY, channel=self._connection.channel(), exchange=exchange)]
        self.task_consumer = TaskConsumer(channel=self._connection.channel(), queues=queues)

    def close_connection(self):
        if not self._connection:
            return

        self._connection.close()
        self._connection = None
        self.task_consumer.close()
        self.task_consumer = None

    def start(self):
        while True:
            self.establish_connection()
            self.consume()
            self.close_connection()

    def stop(self):
        self.close_connection()

    def consume(self):
        """
        消费消息
        :return:
        """
        print("task listener")
        logging.info("task queue start...")
        while True:
            task_msg = self.task_consumer.qos()
            if task_msg:
                self.ready_queue.put(task_msg)
                break
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
        print("task queue listener")
        logging.info("task queue listener start...")
        while True:
            try:
                task_msg = self.ready_queue.get(timeout=1)
                if task_msg:
                    task = TaskManager.to_task(task_msg)
                    self.process_callback(task)
                    self.ready_queue.task_done()
            except Empty:
                pass

    def stop(self):
        self.join()
