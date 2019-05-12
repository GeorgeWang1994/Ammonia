#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-11
@file:      database.py
@contact:   georgewang1994@163.com
@desc:      提供获取任务信息的基础调用函数
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, exc

from ammonia.backends import settings
from .models import Task, TaskStatusChoice


class DbBackend(object):
    """
    利用数据库实现消息持久化
    """
    def __init__(self, backend_url=settings.BACKEND_URL, encoding=settings.BACKEND_ENCODING):
        engine = create_engine(backend_url, encoding=encoding)
        db_session = sessionmaker(bind=engine)
        self.session = db_session()

    def get_task(self, task_id):
        try:
            return self.session.query(Task).filter(Task.task_id == task_id).one()
        except exc.MultipleResultsFound:
            return None

    def get_tasks_by_status(self, status):
        if not status:
            return []

        if status not in TaskStatusChoice.value:
            return []

        return self.session.query(Task).filter(Task.status == status).all()

    def get_tasks_by_ids(self, task_id_list):
        if not task_id_list:
            return []

        return self.session.query(Task).filter(Task.task_id.in_([task_id_list])).all()

    def insert_task(self, status=TaskStatusChoice.START, result=""):
        if status not in TaskStatusChoice.value:
            return False

        self.session.add(Task(status=status, result=result))
        return True

    def update_task_status(self, task_id, status):
        if not task_id:
            return False

        if status not in TaskStatusChoice.value:
            return False

        task = self.get_task(task_id)
        if not task:
            return False

        task.status = status
        self.session.commit()
        return True

    def get_error_tasks(self):
        return self.session.query(Task).filter(Task._traceback.isnot(None)).all()

    def del_task(self, task_id):
        task = self.get_task(task_id)
        if not task:
            return False

        self.session.delete(task)
        self.session.commit()
        return True
