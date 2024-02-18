#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    sse_core.py
    ~~~~~~~~~~~~~~~~~~~~~~~

    sse消息推送和订阅逻辑

    :author: Tangshimin
    :copyright: (c) 2024, Tungee
    :date created: 2024-01-29

"""
import threading

from .sse_clients_global import sse_clients_global
from .sse_redis_pub_sub import sse_redis_pub_sub


class Sse(object):
    def __init__(self):
        pass

    @staticmethod
    def get_channel():
        """
        获取当前连接订阅sse的频道号
        """
        return sse_redis_pub_sub.get_channel()

    @staticmethod
    def connect(channel):
        """
        添加连接对象
        :param channel: 连接id
        """
        return sse_clients_global.connect(channel)

    @staticmethod
    def listen():
        if not sse_clients_global.is_running:
            sse_clients_global.is_running = True
            sse_redis_pub_sub.listen()

    @staticmethod
    def subscribe_message(channel, extra=None):
        """
        订阅sse消息, 添加信息到redis订阅频道
        """
        sse_redis_pub_sub.subscribe(
            channel=channel,
            extra=extra
        )

        return sse_clients_global.listen_message(channel)

    @staticmethod
    def publish_message(channel, data, event=None, _id=None, retry=None):
        """
        推送sse消息, 添加信息到redis发布队列记录
        """
        return sse_redis_pub_sub.publish_message(
            channel=channel,
            data=data,
            event=event,
            _id=_id,
            retry=retry
        )

    @staticmethod
    def heartbeat():
        """
        心跳
        """
        return sse_redis_pub_sub.send_sse_heartbeat()

    @staticmethod
    def sse_run():
        thread = threading.Thread(target=Sse.listen)
        thread.start()
