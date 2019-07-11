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

from ammonia.base.registry import task_registry


class Schedule(threading.Thread):
    """
    每隔一段时间检查是否存在符合时间的任务执行
    """
    def __init__(self, ready_queue, *args, **kwargs):
        super(Schedule, self).__init__(*args, **kwargs)
        self.daemon = True
        self.ready_queue = ready_queue
        self.time_task_list = []  # 存储设置了时间的任务
        self.last_sync_time = None

    def sort_tasks(self):
        self.time_task_list.sort(key=lambda x: x.start_time)

    def get_need_execute_tasks(self, start_time):
        result = []
        next_internal_time = None

        # 计算需要执行的任务，并且将其删除，以及需要等待下一个任务的间隔时间
        for idx in range(len(self.time_task_list))[::-1]:
            task = self.time_task_list[idx]
            if start_time < task.start_time < start_time + datetime.timedelta(seconds=1):
                result.append(task)
                del self.time_task_list[idx]

            # 倒序后首次出现的下一个任务即需要执行的下一个任务
            if not next_internal_time:
                next_task = self.time_task_list[idx + 1] if idx + 1 < len(self.time_task_list) else None
                if next_task:
                    next_internal_time = (next_task.start_time - start_time).total_seconds()

        # 默认等待很长的时间
        if next_internal_time is None:
            next_internal_time = 1000

        return result, next_internal_time

    def run(self):
        print("schedule start running...")
        for task in task_registry.values():
            if task.eta or task.wait:
                self.time_task_list.append(task)

        print("schedule check [%s] execute tasks" % (len(self.time_task_list)))
        while True:
            self.sort_tasks()
            start_time = datetime.datetime.now()

            execute_tasks, next_internal_time = self.get_need_execute_tasks(start_time)
            print("schedule found [%s] tasks and wait [%s] seconds" % (len(execute_tasks), next_internal_time))
            for task in execute_tasks:
                self.ready_queue.put(task.data())  # todo: 可能时间不准，因为read_queue还是可能会有等待的时间

            print("schedule execute task from start_time:[%s] to end_time:[%s]" % (self.last_sync_time, start_time))
            self.last_sync_time = start_time
            time.sleep(next_internal_time)

    def stop(self):
        self.join()
