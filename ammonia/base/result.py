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
    def __init__(self, task_id, *args, **kwargs):
        self.task_id = task_id

    def get(self):
        pass
