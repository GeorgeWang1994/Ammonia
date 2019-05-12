#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-11
@file:      database.py
@contact:   georgewang1994@163.com
@desc:      提供获取任务信息的基础调用函数
"""

import pickle

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, exc

from ammonia.backends import settings
from ammonia import settings as global_settings
from .models import Task, TaskStatusChoice


class DbBackend(object):
    """
    利用数据库实现消息持久化
    """
    def __init__(self, backend_url=settings.BACKEND_URL, encoding=settings.BACKEND_ENCODING):
        self.engine = create_engine(backend_url, encoding=encoding, echo=global_settings.DEBUG)
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
