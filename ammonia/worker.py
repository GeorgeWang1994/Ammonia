#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-06-16
@file:      worker.py
@contact:   georgewang1994@163.com
@desc:      worker
"""

from optparse import OptionParser


def parse_options():
    usage = "python --worker=1"

    parser = OptionParser()

    parser.add_option("-w", "--worker", dest="worker", help="运行worker的个数")

    (options, args) = parser.parse_args()
    return options


class Worker(object):
    pass
