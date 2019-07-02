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

# 命令提示信息
USAGE_MSG = "python --worker 10(worker count) --project example(your_project_name)"


def parse_options(arguments):
    parser = ArgumentParser(usage=USAGE_MSG)

    parser.add_argument("-w", "--worker", dest="worker_num", default=3, type=int, help="运行worker的个数")
    parser.add_argument("-p", "--project", dest="project_name", default="", type=str, help="项目名称")

    args = parser.parse_args(args=arguments)
    return args


# 启动信息
START_UP_MSG = """
tasks: {tasks}
"""


class Worker(object):

    def __init__(self, worker_num=10, project_name=""):
        self.project_name = project_name
        self.worker_controller = WorkerController(pool_worker_count=worker_num)
        self.loader = Loader()

    def setup(self):
        result = self.loader.find_tasks(self.project_name)
        print(START_UP_MSG.format(tasks=result))

    def run(self):
        self.worker_controller.start()
