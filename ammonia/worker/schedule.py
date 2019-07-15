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
        self.start_task_list.sort(key=lambda x: x.start_time)

    def register_task(self, task):
        # todo: 排序
        self.start_task_list.append(task)
        self.sort_tasks()

    def get_need_execute_tasks(self, start_time):
        result = []
        next_internal_time = None

        # 计算需要执行的任务，并且将其删除，以及需要等待下一个任务的间隔时间
        for idx in range(len(self.start_task_list))[::-1]:
            task = self.start_task_list[idx]
            if start_time < task.start_time < start_time + datetime.timedelta(seconds=1):
                result.append(task)
                del self.start_task_list[idx]

            # 倒序后首次出现的下一个任务即需要执行的下一个任务
            if not next_internal_time:
                next_task = self.start_task_list[idx + 1] if idx + 1 < len(self.start_task_list) else None
                if next_task:
                    next_internal_time = (next_task.start_time - start_time).total_seconds()

        # 默认等待很长的时间
        if next_internal_time is None:
            next_internal_time = 1

        return result, next_internal_time

    def run(self):
        print("schedule start running...")
        while True:
            print("schedule check [%s] execute tasks of %s" % (len(self.start_task_list), self.start_task_list))
            if not self.start_task_list:
                time.sleep(1)
                continue

            start_time = datetime.datetime.now()

            execute_tasks, next_internal_time = self.get_need_execute_tasks(start_time)
            if not execute_tasks:
                time.sleep(next_internal_time)
                continue

            print("schedule found [%s] tasks and wait [%s] seconds" % (len(execute_tasks), next_internal_time))
            for task in execute_tasks:
                self.ready_queue.put(task)  # todo: 可能时间不准，因为read_queue还是可能会有等待的时间

            print("schedule execute task from start_time:[%s] to end_time:[%s]" % (self.last_sync_time, start_time))
            self.last_sync_time = start_time

    def stop(self):
        self.join()
