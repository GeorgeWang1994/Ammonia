#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-07-23
@file:      signals.py
@contact:   georgewang1994@163.com
@desc:      信号的定义
"""


from ammonia.utils.signal import Signal


# worker相关

worker_start = Signal("worker_start", must_args=('worker_controller', ))

worker_stop = Signal("worker_stop", must_args=('worker_controller', ))

# 任务相关

task_prepare = Signal("task_prepare", must_args=('task_id', 'task_name', 'exe_args', 'exe_kwargs'))

task_process = Signal("task_process", must_args=('task_id', 'task_name', 'exe_args', 'exe_kwargs'))

task_success = Signal("task_success", must_args=('task_id', 'task_name', 'exe_args', 'exe_kwargs'))

task_fail = Signal("task_fail", must_args=('task_id', 'task_name', 'exe_args', 'exe_kwargs'))

task_retry = Signal("task_retry", must_args=('task_id', 'task_name', 'exe_args', 'exe_kwargs'))
