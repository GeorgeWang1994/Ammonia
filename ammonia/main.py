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

from ammonia.base.loader import Loader
from ammonia.worker.controller import WorkerController


def parse_options(arguments):
    usage = "python --worker=1"

    parser = ArgumentParser(usage=usage)

    parser.add_argument("-w", "--worker", dest="worker_num", default=3, type=int, help="运行worker的个数")
    parser.add_argument("-p", "--project", dest="project_name", type=str, help="项目名称")

    (options, args) = parser.parse_args(args=arguments)
    return options


class Worker(object):

    def __init__(self, worker_num=10, project_name=""):
        self.project_name = project_name
        self.worker_controller = WorkerController(pool_worker_count=worker_num)
        self.loader = Loader()

    def setup(self):
        self.loader.find_tasks(self.project_name)

    def run(self):
        self.worker_controller.start()
