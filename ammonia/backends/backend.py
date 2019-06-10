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

from kombu import Producer, Consumer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, exc

from ammonia import settings
from ammonia.backends.models import Task, TaskStatusChoice
from ammonia.mq import backend_connection, backend_queues

# 队列名字
QUEUE_NAME = "backend_queue"

# 交换器名字
EXCHANGE_NAME = "backend_exchange"


class BaseBackend(object):
    def __init__(self, backend_url):
        self.backend_url = backend_url

    def insert_task(self, task_id, status=TaskStatusChoice.START, result="", traceback=""):
        """
        添加任务
        :param task_id:
        :param status:
        :param result:
        :param traceback:
        :return:
        """
        return NotImplemented

    def get_task(self, task_id):
        """
        返回任务
        :param task_id:
        :return:
        """
        return NotImplemented

    def establish_connection(self):
        """
        建立连接
        :return:
        """
        return NotImplemented

    def close_connection(self):
        """
        关闭连接
        :return:
        """
        return NotImplemented


class MQBackend(BaseBackend):
    """
    利用mq自身功能实现消息持久化
    """
    def __init__(self, backend_url=settings.BACKEND_URL):
        super(MQBackend, self).__init__(backend_url=backend_url)
        self._connection = None
        self.backend_url = backend_url
        self._cache = {}

    def establish_connection(self):
        if not self._connection:
            self._connection = backend_connection
            self._connection.connect()

        return self._connection

    def close_connection(self):
        if self._connection:
            self._connection.close()

        self._connection = None

    def producer(self):
        if not self._connection:
            self.establish_connection()

        return Producer(channel=self._connection.channel, serializer='pickle')

    def consumer(self, task_callback):
        if not self._connection:
            self.establish_connection()

        return Consumer(channel=self._connection, queues=backend_queues, no_ack=False,
                        callbacks=task_callback)

    def insert_task(self, task_id, status=TaskStatusChoice.START, result="", traceback=""):
        if not task_id or not status:
            return False

        producer = self.producer()

        task_dict = {
            "task_id": task_id,
            "status": status,
            "result": result,
            "traceback": pickle.dumps(traceback),
        }
        producer.publish(task_dict, exchange=self._connection.exchange,
                         routing_key=QUEUE_NAME, declare=backend_queues)
        producer.close()
        return True

    def get_task(self, task_id):
        if not task_id:
            return False

        result = []  # 利用可变数据记录结果

        def process_task_callback(body, message):
            print("task_content %s" % body)
            message.ack()
            result.append(body)

        consumer = self.consumer(process_task_callback)
        consumer.consume()
        consumer.close()
        self._cache[task_id] = result[0] if result else None
        return True


class DbBackend(BaseBackend):
    """
    利用数据库实现消息持久化
    """
    def __init__(self, backend_url=settings.BACKEND_URL):
        super(DbBackend, self).__init__(backend_url)
        self.engine = create_engine(backend_url, echo=settings.DEBUG)
        db_session = sessionmaker(bind=self.engine)
        self.session = db_session()

    def get_task(self, task_id):
        try:
            return self.session.query(Task).filter(Task.task_id == task_id).one()
        except exc.MultipleResultsFound:
            return None

    def get_tasks_by_status(self, status):
        if not status:
            return []

        if status not in TaskStatusChoice:
            return []

        return self.session.query(Task).filter(Task.status == status).all()

    def get_tasks_by_ids(self, task_id_list):
        if not task_id_list:
            return []

        return self.session.query(Task).filter(Task.task_id.in_([task_id_list])).all()

    def insert_task(self, task_id, status=TaskStatusChoice.START, result="", traceback=""):
        if status not in TaskStatusChoice:
            return False

        import json
        _traceback = json.dumps(traceback) if traceback else ""
        self.session.add(Task(task_id=task_id, status=status, result=result, _traceback=_traceback))
        self.session.commit()
        return True

    def update_task_status(self, task_id, status):
        if not task_id:
            return False

        if status not in TaskStatusChoice:
            return False

        task = self.get_task(task_id)
        if not task:
            return False

        task.status = status
        self.session.commit()
        return True

    def get_error_tasks(self):
        return self.session.query(Task).filter(Task._traceback != "").all()

    def del_task(self, task_id):
        task = self.get_task(task_id)
        if not task:
            return False

        self.session.delete(task)
        self.session.commit()
        return True


TYPE_2_BACKEND_CLS = {
    'amqp': MQBackend,
    'database': DbBackend,
}


def get_backend_by_settings():
    """
    获取backend
    :param type:
    :return:
    """
    backend_cls = TYPE_2_BACKEND_CLS.get(settings.BACKEND_TYPE or "amqp")
    return backend_cls()


default_backend = get_backend_by_settings()
