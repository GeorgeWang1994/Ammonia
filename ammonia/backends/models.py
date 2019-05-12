#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-11
@file:      models.py
@contact:   georgewang1994@163.com
@desc:      表存储
"""

import datetime
import pickle
from enum import Enum

from sqlalchemy import Column, String, TEXT, Enum as Sql_Enum, DATETIME
from sqlalchemy.ext.declarative import declarative_base

from ammonia.exception import SerializeException

BASE = declarative_base()


class TaskStatusChoice(Enum):
    START = 1
    PROCESSING = 2
    FINISH = 3


class Task(BASE):
    __tablename__ = "task"

    task_id = Column(String(50), primary_key=True, comment=u"任务id")
    status = Column(Sql_Enum(TaskStatusChoice), comment=u"任务当前的状态", nullable=False,
                    default=TaskStatusChoice.START)
    result = Column(String(200), comment=u"任务执行的结果", default="")
    _traceback = Column(TEXT, comment=u"报错信息", default="")
    create_time = Column(DATETIME, comment=u"创建时间", default=datetime.datetime.now(), nullable=False)
    modified_time = Column(DATETIME, comment=u"修改时间", default=datetime.datetime.now(), nullable=False)

    def __repr__(self):
        return "task:%s|%s" % (self.task_id, self.status)

    @property
    def traceback(self):
        if not self._traceback:
            return ""

        try:
            return pickle.loads(self._traceback)
        except SerializeException:
            return ""

    @traceback.setter
    def traceback(self, traceback=""):
        self._traceback = pickle.dumps(traceback)
