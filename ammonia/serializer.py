#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-05-19
@file:      serializer.py
@contact:   georgewang1994@163.com
@desc:      序列化封装
"""
import zlib
from importlib import import_module


class Serializer(object):
    def __init__(self, default_module='pickle'):
        try:
            serializer_model = import_module(default_module)
            self._serializer = serializer_model
        except ImportError:
            raise ImportError(u"导入序列化模块失败")

    def dumps(self, data):
        return zlib.compress(self._serializer.dumps(data))

    def loads(self, data):
        return self._serializer.loads(zlib.decompress(data))


serializer = Serializer()
