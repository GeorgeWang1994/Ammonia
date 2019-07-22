#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@author:    george wang
@datetime:  2019-07-23
@file:      signal.py
@contact:   georgewang1994@163.com
@desc:      信号机制的实现
"""

import hashlib
import weakref
from collections import defaultdict
from functools import wraps


def random_str():
    return "random_str"


def generate_key(value):
    md5 = hashlib.md5()
    md5.update(str(value).encode(encoding='utf-8'))
    return md5.hexdigest()


class Signal(object):
    # 接收方列表
    id_2_receiver_dict = None
    # 信号名字
    name = None
    # 必须提供的参数
    must_args = None
    # 默认的发送方
    default_sender = None

    def __init__(self, name=None, must_args=None, *args, **kwargs):
        self.name = name or random_str()
        self.must_args = must_args or {}
        self.id_2_receiver_dict = defaultdict(dict)
        self.default_sender = "default_sender"

    def __repr__(self):
        return f"signal:{self.name}"

    def connect(self, receiver, sender=None, receiver_id=None):
        if not receiver and not receiver_id:
            raise Exception("接收方不允许为空")

        if not callable(receiver):
            raise Exception("接收方无法调用")

        receiver_id = generate_key(receiver) if not receiver_id else receiver_id
        sender_id = generate_key(sender) if sender else self.default_sender

        receiver_dict = self.id_2_receiver_dict[sender_id]
        if receiver_id in receiver_dict:
            raise Exception(u"已经注册过")

        weakref.finalize(receiver, self.receiver_callback, receiver_id, sender_id)
        receiver = weakref.ref(receiver)
        self.id_2_receiver_dict[sender_id][receiver_id] = receiver

    def receiver_callback(self, receiver_id, sender_id):
        receiver_dict = self.id_2_receiver_dict[sender_id]
        if receiver_id not in receiver_dict:
            return

        del receiver_dict[receiver_id]

    def disconnect(self, receiver, receiver_id=None, sender=None):
        if not receiver and not receiver_id:
            raise Exception("接收方不允许为空")

        receiver_id = generate_key(receiver) if not receiver_id else receiver_id
        sender_id = generate_key(sender) if sender else self.default_sender

        self.receiver_callback(receiver_id, sender_id)

    def send(self, sender, receiver=None, receiver_id=None, *args, **kwargs):
        if receiver or receiver_id:
            receiver_id = generate_key(receiver) if not receiver_id else receiver_id
        sender_id = generate_key(sender) if sender else self.default_sender

        receiver_dict = self.id_2_receiver_dict[sender_id]
        if receiver_id:
            if receiver_id not in receiver_dict:
                raise KeyError(u"并没有注册过")

            receiver_dict[receiver_id]()(sender, *args, **kwargs)
        else:
            for _, receiver in receiver_dict.items():
                receiver()(sender, *args, **kwargs)


subscribe_course = Signal("subscribe_course")


def receiver(signals, sender, receiver_id=None):
    if not signals:
        raise Exception("信号为空")

    def decorator(func):
        for signal in signals:
            signal.connect(func, sender, receiver_id=receiver_id)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator
