#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-11
@file:      backend.py
@contact:   georgewang1994@163.com
@desc:      RabbitMq的持久化，其是通过设置参数durable=True实现的
"""

import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, exc

from ammonia import settings
from ammonia.backends.models import Task
from ammonia.mq import backend_connection, BackendConsumer, BackendProducer
from ammonia.state import TaskStatusEnum

# 队列名字
QUEUE_NAME = "backend_queue"

# 交换器名字
EXCHANGE_NAME = "backend_exchange"


class BaseBackend(object):
    def __init__(self, backend_url):
        self.backend_url = backend_url

    def mark_task_success(self, task_id, result=None):
        """
        标记任务为已经完成
        :param task_id:
        :param result:
        :param trace:
        :return:
        """
        return NotImplemented

    def mark_task_fail(self, task_id, result=None):
        """
        标记任务为失败
        :param task_id:
        :param result:
        :param trace:
        :return:
        """
        return NotImplemented

    def get_task_result(self, task_id, timeout=None):
        """
        返回任务的结果
        :param task_id:
        :param timeout: 阻塞时间（None表示不阻塞直接拿，0表示无限阻塞，其余为阻塞秒数）
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

        return BackendProducer()

    def consumer(self, task_id, task_callback):
        if not self._connection:
            self.establish_connection()

        return BackendConsumer(routing_key=task_id, callbacks=task_callback)

    def _insert_task(self, task_id, status=TaskStatusEnum.CREATED.value, result=None, traceback=None):
        if not task_id or status not in TaskStatusEnum:
            return False

        producer = self.producer()

        task_dict = {
            "task_id": task_id,
            "status": status,
            "result": result,
            "traceback": traceback,
        }
        # 默认发送初始化时候的路由队列
        producer.publish_task(task_dict)
        producer.close()
        return True

    def mark_task_success(self, task_id, result=None):
        if not task_id:
            return False

        self._insert_task(task_id=task_id, status=TaskStatusEnum.SUCCESS.value, result=result)

    def mark_task_fail(self, task_id, result=None):
        if not task_id:
            return False

        self._insert_task(task_id=task_id, status=TaskStatusEnum.FAIL.value, traceback=result)

    def get_task_result(self, task_id, timeout=None):
        if not task_id:
            return False, None

        result = []  # 利用可变数据记录结果

        def process_task_callback(body, message):
            print("task_content %s" % body)
            message.ack()
            result.append(body)

        consumer = self.consumer(task_id, process_task_callback)
        sleep_time = 0

        while True:
            result = consumer.qos(prefetch_count=1)
            if result:
                break
            else:
                if timeout is None:
                    break

                if timeout and sleep_time >= timeout:
                    break

                time.sleep(1)
                sleep_time += 1

        consumer.close()

        if not result:
            return True, None

        result = result[0]
        status = result["status"]
        if status == TaskStatusEnum.FAIL.value:
            return True, result["traceback"]

        return True, result["result"]


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

        if status not in TaskStatusEnum:
            return []

        return self.session.query(Task).filter(Task.status == status).all()

    def get_tasks_by_ids(self, task_id_list):
        if not task_id_list:
            return []

        return self.session.query(Task).filter(Task.task_id.in_([task_id_list])).all()

    def _insert_task(self, task_id, status=TaskStatusEnum.CREATED.value, result=None, traceback=None):
        if not task_id or status not in TaskStatusEnum:
            return False

        self.session.add(Task(task_id=task_id, status=status, result=result, _traceback=traceback))
        self.session.commit()
        return True

    def _update_task_status(self, task_id, status):
        if not task_id:
            return False

        if status not in TaskStatusEnum:
            return False

        task = self.get_task(task_id)
        if not task:
            return False

        task.status = status
        self.session.commit()
        return True

    def mark_task_success(self, task_id, result=None):
        if not task_id:
            return False

        self._insert_task(task_id=task_id, status=TaskStatusEnum.SUCCESS.value, result=result)

    def mark_task_fail(self, task_id, result=None):
        if not task_id:
            return False

        self._insert_task(task_id=task_id, status=TaskStatusEnum.FAIL.value, traceback=result)

    def get_task_result(self, task_id, timeout=None):
        if not task_id:
            return False, None

        while True:
            task = self.get_task(task_id)
            if not task:
                return False, None

            if task.status == TaskStatusEnum.FAIL.value:
                return True, task.traceback

            return True, task.result


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
