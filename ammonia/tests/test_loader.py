#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-07-01
@file:      test_loader.py
@contact:   georgewang1994@163.com
@desc:      ...
"""

import os
import shutil
from unittest import TestCase

from ammonia.base.loader import Loader


class TestLoader(TestCase):

    def setUp(self):
        self.package_name = "example_for_loader_test"
        test_path = os.getcwd()
        self.example_path = os.path.join(test_path, self.package_name)
        if os.path.exists(self.example_path):
            shutil.rmtree(self.example_path)
        os.mkdir(self.example_path)
        with open(os.path.join(self.example_path, "__init__.py"), "w+") as p:
            pass

    def test_find_tasks(self):
        loader = Loader()
        mod_list = loader.find_tasks(self.package_name)
        self.assertEqual(len(mod_list), 0)
        with open(os.path.join(self.example_path, "tasks.py"), "w+") as fp:
            fp.write("""
def get_sum(a, b):
    return a + b""")
        mod_list = loader.find_tasks(self.package_name)
        self.assertEqual(len(mod_list), 1)
        self.assertEqual(mod_list[0].get_sum(1, 2), 3)

    def tearDown(self):
        shutil.rmtree(self.example_path)
