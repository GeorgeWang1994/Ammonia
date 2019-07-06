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

from sqlalchemy import Column, String, DATETIME, BLOB
from sqlalchemy.ext.declarative import declarative_base

from ammonia.state import TaskStatusEnum

# 创建对象的基类:
Base = declarative_base()


class Task(Base):
    __tablename__ = "task"

    task_id = Column(String(100), primary_key=True, comment=u"任务id")
    status = Column(String(50), comment=u"任务当前的状态", nullable=False, default=TaskStatusEnum.CREATED.value)
    _result = Column(BLOB, comment=u"任务执行的结果", default=b"", nullable=True)
    _traceback = Column(BLOB, comment=u"报错信息", default=b"", nullable=True)
    create_time = Column(DATETIME, comment=u"创建时间", default=datetime.datetime.now(), nullable=False)
    modified_time = Column(DATETIME, comment=u"修改时间", default=datetime.datetime.now(), nullable=False)

    def __repr__(self):
        return "task:%s|%s" % (self.task_id, self.status)

    @property
    def result(self):
        if not self._result:
            return ""

        try:
            return pickle.loads(self._result)
        except TypeError:
            return ""

    @result.setter
    def result(self, result=""):
        self._result = pickle.dumps(result, protocol=pickle.HIGHEST_PROTOCOL)

    @property
    def traceback(self):
        if not self._traceback:
            return ""

        try:
            return pickle.loads(self._traceback)
        except TypeError:
            return ""

    @traceback.setter
    def traceback(self, traceback=""):
        self._traceback = pickle.dumps(traceback, protocol=pickle.HIGHEST_PROTOCOL)
