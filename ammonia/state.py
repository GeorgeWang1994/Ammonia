#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-06-12
@file:      state.py
@contact:   georgewang1994@163.com
@desc:      状态机
"""

from enum import Enum, unique


@unique
class TaskStatusEnum(Enum):
    CREATED = "created"  # 初始创建
    PREPARE = "prepare"  # 准备处理
    PROCESS = "process"  # 正在处理
    SUCCESS = "success"  # 处理成功
    FAIL = "fail"        # 处理失败
    RETRY = "retry"        # 重试

    @classmethod
    def all_values(cls):
        return cls._value2member_map_.keys()
