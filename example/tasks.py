#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-06-30
@file:      tasks.py
@contact:   georgewang1994@163.com
@desc:      ...
"""


import datetime

from .ammonia import ammonia


@ammonia.task(eta=datetime.datetime.now() + datetime.timedelta(seconds=10))
def get_abc(a, b):
    return a + b


@ammonia.task(wait=datetime.timedelta(seconds=5))
def get_abc2(a, b):
    return a + b


@ammonia.task()
def get_abc3(a, b):
    return a + b
