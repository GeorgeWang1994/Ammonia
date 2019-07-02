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


# ---------------------------------- task mq ---------------------------------- #


class TaskConnection(Connection):
    hostname = settings.TASK_URL


class TaskExchange(Exchange):
    def __init__(self, name=None, channel=None, *args, **kwargs):
        super(TaskExchange, self).__init__(name=name, channel=channel, *args, **kwargs)


class TaskQueue(Queue):
    def __init__(self, name=None, routing_key=None, exchange=None, channel=None, *args, **kwargs):
        super(TaskQueue, self).__init__(
            name=name, exchange=exchange, routing_key=routing_key,
            channel=channel, *args, **kwargs
        )


task_exchange = TaskExchange(name=settings.TASK_EXCHANGE_NAME)
task_queues = [
    TaskQueue(name=settings.HIGH_TASK_QUEUE_NAME, routing_key=settings.HIGH_TASK_ROUTING_KEY, exchange=task_exchange),
    TaskQueue(name=settings.MID_TASK_QUEUE_NAME, routing_key=settings.MID_TASK_ROUTING_KEY, exchange=task_exchange),
    TaskQueue(name=settings.LOW_TASK_QUEUE_NAME, routing_key=settings.LOW_TASK_ROUTING_KEY, exchange=task_exchange),
]


class TaskConsumer(Consumer):
    def __init__(self, channel=None, queues=None, *args, **kwargs):
        super(TaskConsumer, self).__init__(channel=channel, queues=queues, *args, **kwargs)


class TaskProducer(Producer):
    def __init__(self, routing_key='', channel=None, exchange=None, *args, **kwargs):
        super(TaskProducer, self).__init__(routing_key=routing_key, channel=channel,
                                           exchange=exchange, *args, **kwargs)

    def publish_task(self, message, routing_key, exchange, declare):
        super(TaskProducer, self).publish(body=message, routing_key=routing_key, exchange=exchange, declare=declare,
                                          serializer='pickle')


# ---------------------------------- backend mq ---------------------------------- #


class BackendConnection(Connection):
    hostname = settings.BACKEND_URL


class BackendExchange(Exchange):
    def __init__(self, channel=None, *args, **kwargs):
        # 默认参数durable为True，auto_delete=False，保证持久化
        super(BackendExchange, self).__init__(channel=channel, *args, **kwargs)


class BackendQueue(Queue):
    def __init__(self, routing_key="", exchange=None, channel=None, *args, **kwargs):
        # 默认参数durable为True，auto_delete=False，保证持久化，并且用完即删除
        super(BackendQueue, self).__init__(
            exchang=exchange, routing_key=routing_key,
            channel=channel, *args, **kwargs
        )


class BackendConsumer(Consumer):
    def __init__(self, routing_key, channel=None, callbacks=None, *args, **kwargs):
        queues = [BackendQueue(routing_key=routing_key, channel=channel)]
        super(BackendConsumer, self).__init__(channel=channel, queues=queues, no_ack=False,
                                              callbacks=callbacks, *args, **kwargs)


class BackendProducer(Producer):
    def __init__(self, routing_key="", channel=None, exchange=None, *args, **kwargs):
        super(BackendProducer, self).__init__(routing_key=routing_key, channel=channel,
                                              exchange=exchange, *args, **kwargs)

    def publish_task(self, message):
        super(BackendProducer, self).publish(body=message, serializer="pickle")
