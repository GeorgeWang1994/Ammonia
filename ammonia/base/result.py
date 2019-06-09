#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-25
@file:      result.py
@contact:   georgewang1994@163.com
@desc:      任务结果封装
"""

from ammonia.base.registry import registry


class AsyncResult(object):
    def __init__(self, task_id, backend):
        self.task_id = task_id
        self.backend = backend

    def _get(self):
        """
        从backend中异步获取task_id对应的结果
        :return:
        """
        task = registry.get(self.task_id)
        if not task:
            raise Exception("task %s not found" % self.task_id)

        self.backend

    def get(self):
        pass
