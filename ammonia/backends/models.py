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

from ammonia.db import db
from ammonia.state import TaskStatusEnum


class Task(db.Model):
    __tablename__ = "task"

    task_id = db.Column(db.String(50), primary_key=True, comment=u"任务id")
    status = db.Column(db.String(50), comment=u"任务当前的状态", nullable=False,
                    default=TaskStatusEnum.CREATED.value)
    result = db.Column(db.TEXT, comment=u"任务执行的结果", default="", nullable=True)
    _traceback = db.Column(db.TEXT, comment=u"报错信息", default="", nullable=True)
    create_time = db.Column(db.DATETIME, comment=u"创建时间", default=datetime.datetime.now(), nullable=False)
    modified_time = db.Column(db.DATETIME, comment=u"修改时间", default=datetime.datetime.now(), nullable=False)

    def __repr__(self):
        return "task:%s|%s" % (self.task_id, self.status)

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
        self._traceback = pickle.dumps(traceback)
