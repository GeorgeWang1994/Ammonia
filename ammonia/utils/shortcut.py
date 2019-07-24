#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-12
@file:      utils.py
@contact:   georgewang1994@163.com
@desc:      基础函数
"""

import random
import uuid

from ammonia import settings


def generate_random_uid():
    return str(uuid.uuid1())


def generate_random_routing_key():
    return random.choice(settings.TASK_ROUTING_KEY_LIST)
