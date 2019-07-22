#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-07-22
@file:      runtests.py
@contact:   georgewang1994@163.com
@desc:      跑测试用例
"""

import sys
import unittest
from argparse import ArgumentParser

from ammonia import tests


def collect_tests():
    suite = unittest.TestSuite()
    module_suite = unittest.TestLoader().loadTestsFromModule(tests)
    suite.addTest(module_suite)
    return suite


def run_tests(suite, verbosity=1):
    runner = unittest.TextTestRunner(verbosity=verbosity)
    results = runner.run(suite)
    return results.failfast, results.errors


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-v', '--verbosity', dest="verbosity", type=int, default=1, help="输出错误详细程度")
    args = parser.parse_args(args=sys.argv[1:])

    tests = collect_tests()
    failures, errors = run_tests(tests, args.verbosity)
    if failures:
        print('-' * 20 + 'failures' + '-' * 20)
        print(failures)

    if errors:
        print('-' * 20 + 'errors' + '-' * 20)
        print(errors)
