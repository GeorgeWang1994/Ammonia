#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-11
@file:      exception.py
@contact:   georgewang1994@163.com
@desc:      错误
"""


class NotRegisterException(Exception):
    def __new__(cls, task_id, *args, **kwargs):
        super(Exception, cls).__new__("任务[%s]未注册" % task_id, *args, **kwargs)


class ExecuteTaskException(Exception):
    def __new__(cls, task_id, *args, **kwargs):
        super(Exception, cls).__new__("任务[%s]执行失败" % task_id, *args, **kwargs)
