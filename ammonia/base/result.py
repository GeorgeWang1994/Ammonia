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

    def _get(self, timeout=None):
        """
        从backend中异步获取task_id对应的结果
        :return:
        """
        is_success, result = self.backend.get_task_result(self.task_id, timeout)
        if not is_success:
            return result

        return result

    def get(self, timeout=None):
        return self._get(timeout=timeout)
