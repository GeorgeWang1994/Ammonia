#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-06-30
@file:      tasks.py
@contact:   georgewang1994@163.com
@desc:      ...
"""


from .ammonia import ammonia


@ammonia.task()
def get_sum(a, b):
    return a + b
