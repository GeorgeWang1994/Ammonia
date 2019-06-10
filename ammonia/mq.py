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


# ---------------------------------- task mq ---------------------------------- #


class TaskConnection(Connection):
    hostname = settings.BACKEND_URL


task_connection = TaskConnection()

task_channel = task_connection.channel()


class TaskExchange(Exchange):
    def __init__(self, name=None, *args, **kwargs):
        super(TaskExchange, self).__init__(name=name, channel=task_channel, *args, **kwargs)


task_exchange = TaskExchange()


class TaskQueue(Queue):
    def __init__(self, name=None, routing_key=None, *args, **kwargs):
        super(TaskQueue, self).__init__(
            name=name, exchang=task_exchange, routing_key=routing_key,
            channel=task_channel, *args, **kwargs
        )


task_queues = [TaskQueue("task1", "task1"), TaskQueue("task2", "task2"), TaskQueue("task3", "task3")]


class TaskConsumer(Consumer):
    def __init__(self, channel=None, *args, **kwargs):
        super(TaskConsumer, self).__init__(channel=channel or task_channel, queues=task_queues, *args, **kwargs)


class TaskProducer(Producer):
    def __init__(self, routing_key='', channel=None, *args, **kwargs):
        super(TaskProducer, self).__init__(routing_key=routing_key, channel=channel or task_channel,
                                           exchange=task_exchange, *args, **kwargs)

    def publish_task(self, message):
        super(TaskProducer, self).publish(body=message)


# ---------------------------------- backend mq ---------------------------------- #


class BackendConnection(Connection):
    hostname = settings.BACKEND_URL


backend_connection = BackendConnection()

backend_channel = backend_connection.channel()


class BackendExchange(Exchange):
    def __init__(self, name=None, *args, **kwargs):
        super(BackendExchange, self).__init__(name=name, channel=backend_channel, *args, **kwargs)


backend_exchange = BackendExchange()


class BackendQueue(Queue):
    def __init__(self, name=None, routing_key=None, *args, **kwargs):
        super(BackendQueue, self).__init__(
            name=name, exchang=task_exchange, routing_key=routing_key,
            channel=backend_channel, *args, **kwargs
        )


backend_queues = [BackendQueue("backend1", "backend1"), BackendQueue("backend2", "backend2"),
                  BackendQueue("backend3", "backend3")]


class BackendConsumer(Consumer):
    def __init__(self, channel=None, *args, **kwargs):
        super(BackendConsumer, self).__init__(channel=channel or backend_channel, queues=backend_queues, *args, **kwargs)


class BackendProducer(Producer):
    def __init__(self, routing_key='', channel=None, *args, **kwargs):
        super(BackendProducer, self).__init__(routing_key=routing_key, channel=channel or backend_channel,
                                              exchange=backend_exchange, *args, **kwargs)

    def publish_task(self, message):
        super(BackendProducer, self).publish(body=message)
