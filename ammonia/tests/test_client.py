#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-06-19
@file:      test.py
@contact:   georgewang1994@163.com
@desc:      ...
"""

from ammonia import settings
from ammonia.app import ammonia


@ammonia.task(routing_key=settings.LOW_TASK_ROUTING_KEY)
def get_sum2(a, b):
    return a + b


if __name__ == "__main__":
    async_result = get_sum2.defer(1, 2)
    # result = async_result.get(timeout=3)
    # import asyncio
    # import threading
    #
    #
    # def task():
    #     print("task")
    #
    #
    # def run_loop_inside_thread(loop):
    #     loop.run_forever()
    #
    #
    # loop = asyncio.get_event_loop()
    # threading.Thread(target=run_loop_inside_thread, args=(loop,)).start()
    # loop.call_soon_threadsafe(task)
