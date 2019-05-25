#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-11
@file:      backend.py
@contact:   georgewang1994@163.com
@desc:      RabbitMq的持久化，其是通过设置参数durable=True实现的
"""

import pickle

from kombu import Connection, Queue, Exchange, Producer, Consumer

from ammonia import settings

# 队列名字
QUEUE_NAME = "backend_queue"

# 交换器名字
EXCHANGE_NAME = "backend_exchange"


class MQBackend(object):
    """
    利用mq自身功能实现消息持久化
    """
    def __init__(self):
        self._exchange = Exchange(EXCHANGE_NAME, durable=True, auto_delete=False)
        self._queue = Queue(QUEUE_NAME, exchange=self._exchange, routing_key=QUEUE_NAME, auto_delelte=False)
        self._connection = Connection(
            hostname=settings.BACKEND_HOSTNAME, userid=settings.BACKEND_USER,
            port=settings.BACKEND_PORT, connect_timeout=settings.BROKER_CONNECTION_TIMEOUT,
        )
        self._connection.connect()
        self._cache = {}

    def producer(self):
        if not self._connection:
            return None

        return Producer(channel=self._connection, serializer='pickle')

    def consumer(self, task_callback):
        if not self._connection:
            return None

        return Consumer(channel=self._connection, queues=[self._queue], no_ack=False,
                        callbacks=task_callback)

    def insert_task(self, task_id, status, result="", traceback=""):
        if not task_id or not status:
            return False

        producer = self.producer()
        if not producer:
            return False

        task_dict = {
            "task_id": task_id,
            "status": status,
            "result": result,
            "traceback": pickle.dumps(traceback),
        }
        producer.publish(task_dict, exchange=self._exchange, routing_key=QUEUE_NAME, declare=[self._queue])
        producer.close()
        return True

    def get_task(self, task_id):
        if not task_id:
            return False

        result = []  # 利用可变数据记录结果

        def process_task_callback(body, message):
            print(body)
            message.ack()
            result.append(body)

        consumer = self.consumer(process_task_callback)
        if not consumer:
            return False

        consumer.consume()
        consumer.close()
        self._cache[task_id] = result[0] if result else None
        return True
