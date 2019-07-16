#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-07-09
@file:      clock.py
@contact:   georgewang1994@163.com
@desc:      定期处理任务
"""

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
        self.start_task_list = [task for task in self.start_task_list if
                                task.start_time >= time.time() and (task.eta or task.wait)]
        self.start_task_list.sort(key=lambda x: x.start_time)

    def register_task(self, task):
        self.start_task_list.append(task)
        self.sort_tasks()

    def run(self):
        print("schedule start running...")
        while True:
            if not self.start_task_list:
                time.sleep(1)
                continue

            start_time = time.time()
            task = self.start_task_list[0]
            if start_time < task.start_time < start_time + 60:
                self.ready_queue.put(self.start_task_list.pop(0))

            # 倒序后首次出现的下一个任务即需要执行的下一个任务
            next_task = self.start_task_list[0] if len(self.start_task_list) else None
            next_internal_time = 1
            if next_task:
                next_internal_time = next_task.start_time - start_time

            next_internal_time = min(next_internal_time, 1)
            print("schedule execute task:[%s] from start_time:[%s] to end_time:[%s]" %
                  (task, start_time, start_time))
            time.sleep(next_internal_time)
            self.last_sync_time = start_time

    def stop(self):
        self.join()
