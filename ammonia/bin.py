#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-06-16
@file:      worker.py
@contact:   georgewang1994@163.com
@desc:      worker
"""

from argparse import ArgumentParser

from ammonia.worker.controller import WorkerController
from tasks import *


def parse_options(arguments):
    usage = "python --worker=1"

    parser = ArgumentParser(usage=usage)

    parser.add_argument("-w", "--worker", dest="worker", default=10, type=int, help="运行worker的个数")

    (options, args) = parser.parse_args(args=arguments)
    return options


class Worker(object):

    def __init__(self, worker=10):
        self.worker_controller = WorkerController(pool_worker_count=worker)

    def setup(self):
        print(get_sum)

    def run(self):
        self.worker_controller.start()
