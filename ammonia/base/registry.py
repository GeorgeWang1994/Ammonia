#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-24
@file:      registry.py
@contact:   georgewang1994@163.com
@desc:      注册任务
"""

from ammonia.exception import NotRegisterException


class Registry(dict):
    """
    任务注册
    """
    def _clean(self):
        self.clear()

    def register(self, task):
        """
        :param task:
        :return:
        """
        self[task.task_name] = task

    def unregister(self, task):
        """
        :param task:
        :return:
        """
        self.pop(task.task_name, None)

    def task(self, task_name):
        """

        :param task_name:
        :return:
        """
        try:
            return self[task_name]
        except NotRegisterException:
            raise NotRegisterException(task_name)


task_registry = Registry()
