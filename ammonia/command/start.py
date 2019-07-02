#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-06-29
@file:      start.py
@contact:   georgewang1994@163.com
@desc:      启动服务
"""

import sys

from ammonia.main import Worker, parse_options


def start():
    args = parse_options(sys.argv[1:])
    worker = Worker(worker_num=args.worker_num, project_name=args.project_name)
    worker.setup()
    worker.run()


if __name__ == "__main__":
    start()
