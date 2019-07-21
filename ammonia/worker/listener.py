#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-25
@file:      listener.py
@contact:   georgewang1994@163.com
@desc:      起线程负责监听消息
"""

import logging
import threading
import time
from queue import Empty

from kombu.mixins import ConsumerMixin

from ammonia.base.task import TaskManager
from ammonia.mq import TaskConnection, task_queues, TaskConsumer

logger = logging.getLogger(__name__)


class TaskConsumerWorker(ConsumerMixin):
    def __init__(self, connection, on_task_message):
        self.connection = connection
        self.on_task_message = on_task_message

    def get_consumers(self, Consumer, channel):
        # prefetch_count 保证每个consumer在同一时间只能获取一个消息，只要该消费者消费完后才再次分发给该消费者
        return [TaskConsumer(channel=channel, queues=task_queues, prefetch_count=1, callbacks=[self.on_task_message],
                             accept=['pickle'])]


class TaskListener(object):
    """
    负责监听consumer，将consumer中的消息给取出来
    """
    def __init__(self, ready_queue, schedule, *args, **kwargs):
        self.task_consumer = None
        self.ready_queue = ready_queue
        self.schedule = schedule
        self._connection = None

    def establish_connection(self):
        from ammonia.app import Ammonia
        if self._connection:
            return

        self._connection = TaskConnection(hostname=Ammonia.conf["TASK_URL"],
                                          connect_timeout=Ammonia.conf["BACKEND_CONNECTION_TIMEOUT"])
        self._connection.connect()

    def close_connection(self):
        if not self._connection:
            return

        self._connection.close()
        self._connection = None

    def start(self):
        self.close_connection()
        self.establish_connection()
        self.consume()

    def stop(self):
        self.close_connection()

    def consume(self):
        """
        消费消息
        :return:
        """
        task_consumer = TaskConsumerWorker(self._connection, self.handle_task_message)
        print("TaskListener: 获取消息中...")
        try:
            task_consumer.run()
        except KeyboardInterrupt:
            print("TaskListener: bye bye")
            self.stop()

    def handle_task_message(self, body, message):
        print("TaskListener: 获取到消息%s" % body)
        eta = body.get("eta", None)
        wait = body.get("wait", None)
        if eta or wait:
            print("TaskListener: register time task")
            self.schedule.register_task(body)
        else:
            print("TaskListener: register now task")
            self.ready_queue.put(body)
        message.ack()


class TaskQueueListener(threading.Thread):
    """
    负责监听ready_queue，将队列中的消息给取出来，加入到协程池
    """
    def __init__(self, ready_queue, pool, *args, **kwargs):
        super(TaskQueueListener, self).__init__(name="task_queue_listener", *args, **kwargs)
        self.setDaemon(True)
        self.ready_queue = ready_queue
        self.pool = pool

    def run(self):
        """
        消费消息
        :return:
        """
        print("TaskQueueListener: task queue listener start...")
        logging.info("TaskQueueListener: task queue listener start...")
        while True:
            try:
                task_msg = self.ready_queue.get()
                if task_msg:
                    print("TaskQueueListener: 获取到消息%s" % task_msg)
                    self.ready_queue.task_done()
                    TaskManager.execute_task(self.pool, task_msg)
            except Empty:
                time.sleep(1)
            except KeyboardInterrupt:
                print("TaskQueueListener: bye bye")

    def stop(self):
        self.join()
