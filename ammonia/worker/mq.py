#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-24
@file:      mq.py
@contact:   georgewang1994@163.com
@desc:      ...
"""

from kombu import Consumer, Producer, Connection, Exchange, Queue

from ammonia import settings

ROUTING_KEY = 'task'


class TaskConnection(Connection):
    hostname = settings.BACKEND_URL


task_connection = TaskConnection()


class TaskExchange(Exchange):
    name = "task_exchange"
    _channel = task_connection.channel()


task_exchange = TaskExchange()


class TaskQueue(Queue):
    name = "task_queue"
    exchange = task_exchange
    _channel = task_connection.channel()
    routing_key = ROUTING_KEY


task_queues = [TaskQueue()]


class TaskConsumer(Consumer):
    queues = task_queues
    channel = task_connection.channel()

    def __init__(self, *args, **kwargs):
        super(TaskConsumer, self).__init__(*args, **kwargs)


class TaskProducer(Producer):
    channel = task_connection.channel()

    def __init__(self, *args, **kwargs):
        super(TaskProducer, self).__init__(*args, **kwargs)

    def publish_task(self, task_manager):
        message = task_manager.to_message()
        super(TaskProducer, self).publish(body=message)
