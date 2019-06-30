#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-06-29
@file:      start.py
@contact:   georgewang1994@163.com
@desc:      ...
"""

import sys

from ammonia.bin import Worker, parse_options

if __name__ == "__main__":
    options = parse_options(sys.argv[1:])
    print("options is %s" % options)
    worker = Worker(**options)
    worker.setup()
    worker.run()
