#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-20
@file:      test_pool.py
@contact:   georgewang1994@163.com
@desc:      测试协程池
"""

import asyncio

from ammonia.backends.worker.pool import AsyncPool


async def example_coro(initial_number, result_queue):
    print("Processing Value! -> {} * 2 = {}".format(initial_number, initial_number * 2))
    await asyncio.sleep(1)
    await result_queue.put(initial_number * 2)


def result_executor(i):
    return i


def success_executor(i):
    print("success", i)


def fail_executor(i):
    print("fail", i)


async def run():

    # Start a worker pool with 10 coroutines, invokes `example_coro` and waits for it to complete or 5 minutes to pass.
    async with AsyncPool(worker_count=2) as pool:
        for i in range(50):
            await pool.apply_async(result_executor, success_executor, fail_executor, i)


result_queue = asyncio.Queue()
loop = asyncio.get_event_loop()
loop.run_until_complete(run())
