#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-20
@file:      test_pool.py
@contact:   georgewang1994@163.com
@desc:      测试协程池
"""

# import asyncio
import time
#
# from ammonia.backends.worker.pool import AsyncPool


def result_executor(i):
    print("%s: 等待1s" % i)
    time.sleep(1)
    return i


def success_executor(i):
    print("success", i)


def fail_executor(i):
    print("fail", i)

#
# async def run():
#     async with AsyncPool(worker_count=10) as pool:
#         for i in range(50):
#             await pool.apply_async(result_executor, success_executor, fail_executor, i)
#
#
# result_queue = asyncio.Queue()
# loop = asyncio.get_event_loop()
# loop.run_until_complete(run())


import asyncio

from ammonia.worker.pool import AsyncPool


async def run():
    async with AsyncPool(10, loop) as pool:
        for i in range(50):
            await pool.apply_async(result_executor, success_executor, fail_executor, i)

loop = asyncio.get_event_loop()

loop.run_until_complete(run())
