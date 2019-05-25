#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-24
@file:      ammonia.py
@contact:   georgewang1994@163.com
@desc:      总控制
"""

from ammonia.worker.controller import WorkerController


class Ammonia(object):

    def __init__(self):
        self.worker_controller = WorkerController()

    def run(self):
        self.worker_controller.start()


ammonia = Ammonia()

if __name__ == '__main__':
    ammonia.run()
