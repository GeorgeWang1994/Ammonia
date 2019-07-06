#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-06-15
@file:      test_base.py
@contact:   georgewang1994@163.com
@desc:      测试用例基类
"""

import contextlib
from unittest import TestCase

import sqlalchemy.exc as sqlalchemy_exc
from sqlalchemy import create_engine
from sqlalchemy.orm import close_all_sessions
from sqlalchemy_utils import database_exists, create_database, drop_database

from ammonia import settings
from ammonia.app import Ammonia
from ammonia.backends.models import Base

ammonia = Ammonia(conf={"BACKEND_URL": settings.TEST_CASE_BACKEND_URL})


class TestDBBackendBase(TestCase):
    def setUp(self):
        with contextlib.suppress(sqlalchemy_exc.ProgrammingError):
            engine = create_engine(settings.TEST_CASE_BACKEND_URL, encoding='utf-8', echo=True)

            if database_exists(engine.url):
                drop_database(settings.TEST_CASE_BACKEND_URL)

            create_database(settings.TEST_CASE_BACKEND_URL)
            Base.metadata.create_all(engine)


    def tearDown(self):
        with contextlib.suppress(sqlalchemy_exc.ProgrammingError):
            engine = create_engine(settings.TEST_CASE_BACKEND_URL, encoding='utf-8', echo=True)

            close_all_sessions()
            if database_exists(engine.url):
                drop_database(settings.TEST_CASE_BACKEND_URL)
