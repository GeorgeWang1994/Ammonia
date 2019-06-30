#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-24
@file:      registry.py
@contact:   georgewang1994@163.com
@desc:      注册任务
"""


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
        self[task.task_id] = task

    def unregister(self, task):
        """
        :param task:
        :return:
        """
        self.pop(task.task_id, None)

    def task(self, task_id):
        """

        :param task_id:
        :return:
        """
        try:
            return self[task_id]
        except KeyError:
            print("task %s not found" % task_id)
            pass


task_registry = Registry()
