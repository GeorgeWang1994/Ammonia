#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-06-29
@file:      tasks.py
@contact:   georgewang1994@163.com
@desc:      ...
"""


from ammonia import settings
from ammonia.app import Ammonia


ammonia = Ammonia()


@ammonia.task(routing_key=settings.LOW_TASK_ROUTING_KEY)
def get_sum(a, b):
    return a + b


@ammonia.task(routing_key=settings.LOW_TASK_ROUTING_KEY)
def get_product(a, b):
    return a * b