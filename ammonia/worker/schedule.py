#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-07-09
@file:      clock.py
@contact:   georgewang1994@163.com
@desc:      定期处理任务
"""

import datetime
import threading
import time


class Schedule(threading.Thread):
    """
    每隔一段时间检查是否存在符合时间的任务执行
    """
    def __init__(self, ready_queue, *args, **kwargs):
        super(Schedule, self).__init__(*args, **kwargs)
        self.setDaemon(True)
        self.ready_queue = ready_queue
        self.start_task_list = []  # 开始执行的任务
        self.last_sync_time = None

    def sort_tasks(self):
        self.start_task_list.sort(key=lambda x: x[0]["start_time"])

    def register_task(self, task_body, task_msg):
        """
        注册定时任务
        :param task_body: 任务数据
        :param task_msg: message
        :return:
        """
        if not task_body.get("start_time"):
            raise KeyError("任务start_time不存在")

        if not task_body.get("eta") and not task_body.get("wait"):
            raise Exception("任务不符合定时任务标准")

        if not task_body["start_time"] < datetime.datetime.now().timestamp():
            raise Exception("任务起始时间小于当前时间")

        if not task_body.get("task_id"):
            raise KeyError("task_id不存在")

        self.start_task_list.append((task_body, task_msg))
        self.sort_tasks()

    def get_need_execute_task(self, start_time):
        task_body, task_msg = self.start_task_list[0]
        task_start_time = task_body["start_time"]
        need_task_body = None
        if start_time < task_start_time < start_time + 1:
            need_task_body = task_body

        # 倒序后首次出现的下一个任务即需要执行的下一个任务
        next_task_body, _ = self.start_task_list[1] if len(self.start_task_list) > 1 else (None, None)
        next_internal_time = None
        if next_task_body:
            next_internal_time = next_task_body["start_time"] - datetime.datetime.now().timestamp()
            next_internal_time = next_internal_time if next_internal_time > 1 else None  # 小于1s，不sleep

        return need_task_body, task_msg, next_internal_time

    def run(self):
        print("schedule start running...")
        while True:
            if not self.start_task_list:
                time.sleep(1)
                continue

            start_time = datetime.datetime.now().timestamp()
            task_body, task_msg, next_internal_time = self.get_need_execute_task(start_time)
            if task_body:
                self.ready_queue.put((task_body, task_msg))
                print("schedule execute task:[%s] from start_time:[%s] to end_time:[%s]" %
                      (task_body, self.last_sync_time, start_time))

            self.last_sync_time = start_time
            if next_internal_time:
                time.sleep(next_internal_time)

    def stop(self):
        self.join()
