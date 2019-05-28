#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-25
@file:      result.py
@contact:   georgewang1994@163.com
@desc:      任务结果封装
"""


class AsyncResult(object):
    def __init__(self, task_id, backend):
        self.task_id = task_id
        self.backend = backend

    def _get(self):
        """
        从backend中异步获取task_id对应的结果
        :return:
        """
        # todo: 异步获取结果

    def get(self):
        pass
