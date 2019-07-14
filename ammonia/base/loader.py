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
import pkgutil
import sys
from contextlib import contextmanager


@contextmanager
def cwd_in_path():
    """将当前工作路径加入到path中"""
    cwd = os.getcwd()
    if cwd in sys.path:
        yield
    else:
        sys.path.insert(0, cwd)
        try:
            yield cwd
        finally:
            try:
                sys.path.remove(cwd)
            except ValueError:  # pragma: no cover
                pass


class BaseLoader(object):

    TASK_MODULE_PREFIX = 'tasks'  # 默认的任务模块

    BASE_PROJECT_PATH = os.getcwd()  # 当前工作路径

    @classmethod
    def find_tasks(cls, project_name):
        return NotImplementedError

    @classmethod
    def on_worker_start(cls, project_name):
        cls.find_tasks(project_name)


class Loader(BaseLoader):

    @classmethod
    def check_modules_equal(cls, path, package_name):
        module_iter = pkgutil.iter_modules([path])
        for module in module_iter:
            if module.name == package_name:
                return True
        return False

    @classmethod
    def get_tasks_from_dictionary(cls, package_name):
        """
        获取到当前目录下的所有以_tasks为结尾的文件
        :param package_name
        :return:
        """
        if not cls.check_modules_equal(cls.BASE_PROJECT_PATH, package_name):
            raise ModuleNotFoundError("在项目中未找到package[%s]，请检查是否是一级目录" % package_name)

        package_path = os.path.join(cls.BASE_PROJECT_PATH, package_name)

        file_list = []
        for dir_path in os.listdir(package_path):
            if not os.path.isfile(os.path.join(package_path, dir_path)):
                continue

            basename = os.path.basename(dir_path)
            if not basename.startswith(cls.TASK_MODULE_PREFIX):
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
        with cwd_in_path():
            for task in task_list:
                task_module = task[:-3]
                try:
                    mod = importlib.import_module("%s.%s" % (project_name, task_module))
                    mod_list.append(mod)
                except ModuleNotFoundError:
                    print("无法从项目【%s】中导入任务模块【%s】" % (project_name, task_module))
                    raise

        return mod_list
