#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-19
@file:      pool.py
@contact:   georgewang1994@163.com
@desc:      ...
"""

import asyncio


class AsyncPool(object):
    """
    协程池
    """
    def __init__(self, worker_count):
        self.worker_count = worker_count
        self.loop = asyncio.get_event_loop()
        self.queue = asyncio.Queue(maxsize=self.worker_count)
        self._workers = []

    def start(self):
        self._workers = [asyncio.ensure_future(self._worker_loop(), loop=self.loop) for _ in range(self.worker_count)]

    def close(self):
        self.loop.close()
        del self.loop
        del self.queue

    def _worker_loop(self):
        pass

    def apply_async(self, executor_func, success_callback=None, error_callback=None, *args, **kwargs):
        future = asyncio.futures.Future(loop=self.loop)
        future.add_done_callback(self.on_receive)
        await self.queue.put((future, args, kwargs))

        return future

    def on_receive(self, success_callback=None, error_callback=None):
        pass

