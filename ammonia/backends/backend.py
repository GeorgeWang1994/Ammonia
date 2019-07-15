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
import time

from redis import Redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, exc

from ammonia import settings
from ammonia.backends.models import Task
from ammonia.mq import BackendConnection, BackendConsumer, BackendProducer
from ammonia.state import TaskStatusEnum

# 队列名字
QUEUE_NAME = "backend_queue"

# 交换器名字
EXCHANGE_NAME = "backend_exchange"


class BaseBackend(object):
    def __init__(self, backend_url, timeout=None):
        self.backend_url = backend_url
        self.timeout = timeout
        self._connection = None

    def mark_task_success(self, task_id, result=None):
        """
        标记任务为已经完成
        :param task_id:
        :param result:
        :return:
        """
        return NotImplemented

    def mark_task_retry(self, task_id, result=None):
        """
        标记任务为重试
        :param task_id:
        :param :
        :param result:
        :return:
        """
        return NotImplemented

    def mark_task_fail(self, task_id, result=None):
        """
        标记任务为失败
        :param task_id:
        :param result:
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
    def __init__(self, backend_url=settings.BACKEND_URL, timeout=None):
        super(MQBackend, self).__init__(backend_url=backend_url, timeout=timeout)

    def establish_connection(self):
        if self._connection:
            return

        if not self._connection:
            self._connection = BackendConnection(hostname=self.backend_url,
                                                 connect_timeout=self.timeout)
            self._connection.connect()

        return self._connection

    def close_connection(self):
        if not self._connection:
            return

        if self._connection:
            self._connection.close()

        self._connection = None

    def producer(self, task_id):
        self.establish_connection()

        return BackendProducer(channel=self._connection, routing_key=task_id)

    def consumer(self, task_id, task_callback):
        self.establish_connection()

        return BackendConsumer(routing_key=task_id, callbacks=task_callback, channel=self._connection)

    def _save_task(self, task_id, status=TaskStatusEnum.CREATED.value, result=None, traceback=None):
        if not task_id or status not in TaskStatusEnum:
            return False

        producer = self.producer(task_id=task_id)

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

        return self._save_task(task_id=task_id, status=TaskStatusEnum.SUCCESS.value, result=result)

    def mark_task_fail(self, task_id, result=None):
        if not task_id:
            return False

        return self._save_task(task_id=task_id, status=TaskStatusEnum.FAIL.value, traceback=result)

    def mark_task_retry(self, task_id, result=None):
        if not task_id:
            return False

        return self._save_task(task_id=task_id, status=TaskStatusEnum.RETRY.value, traceback=result)

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
    def __init__(self, backend_url=settings.BACKEND_URL, timeout=None):
        super(DbBackend, self).__init__(backend_url=backend_url, timeout=timeout)
        self._sessionmaker = None
        self._db = None

    def establish_connection(self):
        if self._db:
            return

        self._db = create_engine(self.backend_url, pool_timeout=self.timeout)
        self._connection = self._db.connect()

    def close_connection(self):
        """
        关闭连接
        :return:
        """
        if not self._db:
            return

        self._sessionmaker.close_all()
        self._connection.close()
        self._db.dispose()
        self._connection = None
        self._sessionmaker = None
        self._db = None

    def create_session(self):
        if self._sessionmaker:
            return self._sessionmaker()

        if not self._db:
            self.establish_connection()

        self._sessionmaker = sessionmaker(bind=self._db)
        return self._sessionmaker()

    def get_task(self, task_id):
        try:
            return self.create_session().query(Task).filter(Task.task_id == task_id).one()
        except (exc.MultipleResultsFound, exc.NoResultFound):
            return None

    def get_tasks_by_ids(self, task_id_list):
        if not task_id_list:
            return []

        return self.create_session().query(Task).filter(Task.task_id.in_([task_id_list])).all()

    def _save_task(self, task_id, status=TaskStatusEnum.CREATED.value, result=None, traceback=None):
        if not task_id or status not in TaskStatusEnum.all_values():
            return False

        if result is not None:
            result = pickle.dumps(result, protocol=pickle.HIGHEST_PROTOCOL)
        elif traceback is not None:
            traceback = pickle.dumps(traceback, protocol=pickle.HIGHEST_PROTOCOL)

        session = self.create_session()
        session.add(Task(task_id=task_id, status=status, _result=result, _traceback=traceback))
        session.commit()
        return True

    def mark_task_retry(self, task_id, result=None):
        if not task_id:
            return False

        return self._save_task(task_id=task_id, status=TaskStatusEnum.RETRY.value, result=result)

    def mark_task_success(self, task_id, result=None):
        if not task_id:
            return False

        return self._save_task(task_id=task_id, status=TaskStatusEnum.SUCCESS.value, result=result)

    def mark_task_fail(self, task_id, result=None):
        if not task_id:
            return False

        return self._save_task(task_id=task_id, status=TaskStatusEnum.FAIL.value, traceback=result)

    def _get_task_result(self, task_id):
        task = self.get_task(task_id)
        if not task:
            return False, None

        if task.status == TaskStatusEnum.FAIL.value:
            return True, task.traceback

        return True, task.result

    def get_task_result(self, task_id, timeout=None):
        if not task_id:
            return False, None

        sleep_time = 0
        while True:
            success, result = self._get_task_result(task_id)
            if success:
                return True, result

            if timeout is None:
                return True, None

            if timeout and sleep_time >= timeout:
                return True, None

            time.sleep(1)
            sleep_time += 1


class RedisBackend(BaseBackend):
    """
    使用redis进行持久化
    """
    def __init__(self, backend_url=settings.BACKEND_URL, timeout=None):
        super(RedisBackend, self).__init__(backend_url=backend_url, timeout=timeout)

    def establish_connection(self):
        if self._connection:
            return

        # todo: redis中不允许直接传URL，需要进行解析
        self._connection = Redis(host="localhost", socket_connect_timeout=self.timeout)

    def close_connection(self):
        """
        关闭连接
        :return:
        """
        if not self._connection:
            return

        self._connection = None

    def _save_task(self, task_id, status, result=None, traceback=None):
        if not task_id or status not in TaskStatusEnum.all_values():
            return False

        if result is not None:
            result = pickle.dumps(result, protocol=pickle.HIGHEST_PROTOCOL)
        elif traceback is not None:
            result = pickle.dumps(traceback, protocol=pickle.HIGHEST_PROTOCOL)

        self._connection.lpush(task_id, result)
        return True

    def mark_task_retry(self, task_id, result=None):
        if not task_id:
            return False

        return self._save_task(task_id=task_id, status=TaskStatusEnum.RETRY.value, result=result)

    def mark_task_success(self, task_id, result=None):
        """
        标记任务为已经完成
        :param task_id:
        :param result:
        :param trace:
        :return:
        """
        if not self._connection:
            self.establish_connection()

        return self._save_task(task_id, TaskStatusEnum.SUCCESS.value, result=result)

    def mark_task_fail(self, task_id, result=None):
        """
        标记任务为失败
        :param task_id:
        :param result:
        :param trace:
        :return:
        """
        if not self._connection:
            self.establish_connection()

        return self._save_task(task_id, TaskStatusEnum.FAIL.value, traceback=result)

    def get_task_result(self, task_id, timeout=None):
        """
        返回任务的结果
        :param task_id:
        :param timeout: 阻塞时间（None表示不阻塞直接拿，0表示无限阻塞，其余为阻塞秒数）
        :return:
        """
        if not self._connection:
            self.establish_connection()
        # 不用轮询的方式是因为在列表可能经常为空的情况下会导致多次请求
        result = self._connection.blpop([task_id], timeout=timeout)
        if result:
            return pickle.loads(result[1])
        return


TYPE_2_BACKEND_CLS = {
    'amqp': MQBackend,
    'database': DbBackend,
    'redis': RedisBackend,
}


def get_backend_by_settings(type="database"):
    """
    获取backend
    :param type:
    :return:
    """
    return TYPE_2_BACKEND_CLS.get(type, DbBackend)
