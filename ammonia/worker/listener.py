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
        if self.task_consumer:
            return

        self._connection = TaskConnection(hostname=Ammonia.conf["TASK_URL"],
                                          connect_timeout=Ammonia.conf["BACKEND_CONNECTION_TIMEOUT"])
        self._connection.connect()
        # prefetch_count 保证每次consumer在同一时间只能获取一个消息
        self.task_consumer = TaskConsumerWorker(self._connection, self.handle_task_message)

    def close_connection(self):
        if not self._connection:
            return

        self.task_consumer.should_stop = True
        self.task_consumer = None
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
        try:
            print("TaskListener: 获取消息中...")
            self.task_consumer.run()
        except KeyboardInterrupt:
            print("TaskListener: bye bye")
            pass

    def handle_task_message(self, body, message):
        print("TaskListener: 获取到消息%s" % body)
        is_package = body.pop("is_package", False)
        exe_task = TaskManager.create_exe_task_or_package(is_package, **body)
        if exe_task.task.eta or exe_task.task.wait:
            self.schedule.register_task(exe_task)
        else:
            self.ready_queue.put(exe_task)
        message.ack()


class TaskQueueListener(threading.Thread):
    """
    负责监听ready_queue，将队列中的消息给取出来，加入到协程池
    """
    def __init__(self, ready_queue, process_callback, loop, *args, **kwargs):
        super(TaskQueueListener, self).__init__(name="task_queue_listener", target=self.consume, *args, **kwargs)
        self.setDaemon(True)
        self.ready_queue = ready_queue
        self.process_callback = process_callback
        self.loop = loop

    def consume(self):
        """
        消费消息
        :return:
        """
        print("task queue listener start...")
        logging.info("task queue listener start...")
        while True:
            try:
                task = self.ready_queue.get()
                if task:
                    print("TaskQueueListener: 获取到消息%s" % task)
                    self.ready_queue.task_done()
                    print("获取到消息中的 args: %s, kwargs: %s" % (task.execute_args, task.execute_kwargs))
                    self.loop.run_until_complete(self.process_callback(task))
            except Empty:
                time.sleep(1)
            except KeyboardInterrupt:
                print("TaskQueueListener: bye bye")

    def stop(self):
        self.join()
