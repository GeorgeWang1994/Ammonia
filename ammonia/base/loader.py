#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-06-30
@file:      discover.py
@contact:   georgewang1994@163.com
@desc:      ...
"""

import importlib
import os
from importlib import util

from ammonia.settings import BASE_PROJECT_PATH, TASK_MODULE_SUFFIX


class BaseLoader(object):

    @classmethod
    def find_tasks(cls, project_name):
        return NotImplementedError

    @classmethod
    def on_worker_start(cls, project_name):
        cls.find_tasks(project_name)


class Loader(BaseLoader):

    @classmethod
    def get_tasks_from_dictionary(cls, package_name):
        """
        获取到当前目录下的所有以_tasks为结尾的文件
        :param package_name
        :return:
        """
        if not util.find_spec(package_name, package="."):
            raise ModuleNotFoundError("在项目中未找到package[%s]，请检查是否是一级目录" % package_name)

        package_path = os.path.join(BASE_PROJECT_PATH, package_name)

        file_list = []
        for dir_path in os.listdir(package_path):
            if not os.path.isfile(os.path.join(package_path, dir_path)):
                continue

            basename = os.path.basename(dir_path)
            if not basename[:-3].endswith(TASK_MODULE_SUFFIX):
                continue

            file_list.append(basename)
        return file_list

    @classmethod
    def find_tasks(cls, project_name):
        """
        寻找项目下的任务
        :param project_name:
        :return:
        """
        task_list = cls.get_tasks_from_dictionary(project_name)
        if not task_list:
            print("在指定的项目【%s】中没有找到任务的任务模块" % project_name)
            return []

        mod_list = []
        for task in task_list:
            task_module = task[:-3]
            try:
                mod = importlib.import_module("%s.%s" % (project_name, task_module))
                mod_list.append(mod)
            except ModuleNotFoundError:
                print("无法导入任务模块【%s】" % task_module)
                pass

        return mod_list
