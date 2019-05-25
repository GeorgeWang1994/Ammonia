#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-24
@file:      registry.py
@contact:   georgewang1994@163.com
@desc:      注册任务
"""


class Registry(object):
    """
    任务注册
    """
    cache = {}

    def __init__(self):
        self._clean()

    def _clean(self):
        self.cache.clear()

    def register(self, task):
        """
        :param task:
        :return:
        """
        self.cache[task.id] = task

    def unregister(self, task):
        """
        :param task:
        :return:
        """
        self.cache.pop(task.id, None)

    def task(self, task_id):
        """

        :param task_id:
        :return:
        """
        return self.cache.get(task_id)


registry = Registry()
