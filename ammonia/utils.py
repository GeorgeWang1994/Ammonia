#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-12
@file:      utils.py
@contact:   georgewang1994@163.com
@desc:      基础函数
"""

import uuid


def generate_random_uid():
    return str(uuid.uuid1())
