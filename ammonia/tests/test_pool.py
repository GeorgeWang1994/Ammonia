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


async def example_coro(initial_number, result_queue):
    # 生产者
    print("Processing Value! -> {} * 2 = {}".format(initial_number, initial_number))
    await asyncio.sleep(1)
    await result_queue.put(initial_number * 2)


async def result_reader(queue):
    # 消费者
    while True:
        value = await queue.get()
        if value is None:
            break
        print("Got value! -> {}".format(value))


async def run():

    result_queue = asyncio.Queue()

    #  创建任务
    reader_future = asyncio.ensure_future(result_reader(result_queue), loop=loop)

    #
    async with AsyncPool(10, loop) as pool:
        for i in range(50):
            await pool.apply_async(example_coro, success_executor, fail_executor, i, result_queue)

    await reader_future

loop = asyncio.get_event_loop()

loop.run_until_complete(run())
