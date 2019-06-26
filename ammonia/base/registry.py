#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-24
@file:      registry.py
@contact:   georgewang1994@163.com
@desc:      注册任务
"""

from collections import UserDict


class Registry(UserDict):
    """
    任务注册
    """
    cache = {}

    def _clean(self):
        self.cache.clear()

    def register(self, task):
        """
        :param task:
        :return:
        """
        self.cache[task.task_id] = task

    def unregister(self, task):
        """
        :param task:
        :return:
        """
        self.cache.pop(task.task_id, None)

    def task(self, task_id):
        """

        :param task_id:
        :return:
        """
        try:
            return self.cache[task_id]
        except KeyError:
            print("task %s not found" % task_id)
            pass


registry = Registry()
