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
import functools
import logging


logger = logging.getLogger(__name__)


class AsyncPool(object):
    """
    协程池
    """
    def __init__(self, worker_count, loop=None):
        self.worker_count = worker_count
        self.loop = loop
        self.queue = asyncio.Queue(maxsize=self.worker_count)
        self._workers = []

    def start(self):
        logger.info("async pool start...")
        print("async pool start...")
        self._workers = [asyncio.ensure_future(self._worker(), loop=self.loop) for _ in range(self.worker_count)]

    async def __aenter__(self):
        self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.join()

    async def stop(self):
        await self.join()
        self.loop.stop()
        self.loop = None

    async def join(self):
        if not self._workers:
            return

        # 等待队列中的数据全部被处理完
        await self.queue.join()
        # 等待所有的worker被取消
        await asyncio.gather(*self._workers, loop=self.loop)
        self._workers = []

    async def _worker(self):
        while True:
            print("pool worker 等待获取消息...")
            item = await self.queue.get()

            future, executor_func, args, kwargs = item
            print("future:[%s], executor_func:[%s], args:[%s], kwargs:[%s]" % (future, executor_func, args, kwargs))
            try:
                result_value = executor_func(*args, **kwargs)
                print("获取到任务的结果:%s" % result_value)
                future.set_result((True, result_value))
            except (KeyboardInterrupt, MemoryError, SystemExit) as e:
                future.set_exception(e)
                print("pool worker: bye bye")
            except Exception as e:
                future.set_result((False, e.args[0]))
            finally:
                self.queue.task_done()

    async def apply_async(self, executor_func, success_callback=None, error_callback=None, *args, **kwargs):
        future = asyncio.futures.Future(loop=self.loop)
        future.add_done_callback(functools.partial(self.on_receive, success_callback, error_callback))
        await self.queue.put((future, executor_func, args, kwargs))
        return future

    def on_receive(self, success_callback, error_callback, future):
        is_success, result_value = future.result()
        print("回调结果为 success: [%s], return value: [%s]" % (is_success, result_value))

        if is_success and success_callback:
            success_callback(result_value)

        if not is_success and error_callback:
            error_callback(result_value)
