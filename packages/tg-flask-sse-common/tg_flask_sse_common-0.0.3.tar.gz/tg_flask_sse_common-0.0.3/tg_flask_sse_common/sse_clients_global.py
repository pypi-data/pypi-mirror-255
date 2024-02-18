#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    sse_clients_global.py
    ~~~~~~~~~~~~~~~~~~~~~~~

    sse全局连接对象

    :author: Tangshimin
    :copyright: (c) 2024, Tungee
    :date created: 2024-01-29

"""
from datetime import datetime
import time

from .sse_constant import SseClientConfig


class SseClientsGlobal(object):
    """
    用于全局保存sse连接对象
    背景 : 因为在每个sse长连接中，每次创建redis-pub-sub监听会耗cpu的操作，所以redis-pub-sub需要全局创建，
          如果全局创建redis-pub-sub，就无法区分不同的sse连接，也就无法对不同的sse连接进行操作，
          所以需要一个全局保存sse连接对象的地方
    原理 : 原理类似websocket的全局socket对象机制，每个连接都保存在了全局socket对象中，通过socket_id进行访问
          主要考虑连接建立时，连接断开时，连接异常时的处理，同时提供定时任务清理无效连接
    连接建立 : 保存连接对象
    连接断开 : 删除连接对象
    连接异常 : 删除连接对象
    """

    class Field(object):
        """
        sse全局连接对象字段
        """
        MESSAGE_LIST = 'message_list'
        CONNECT_TIME = 'connect_time'

    def __init__(self):
        self.is_running = False
        self.sse_global_clients = {}
        # 控制连接最大时间，超过时间超过定时任务清理
        self.max_connect_time = SseClientConfig.MAX_CONNECT_TIME
        self.max_connect_count = SseClientConfig.MAX_CONNECT_COUNT
        self.listen_interval = SseClientConfig.LISTEN_INTERVAL

    def count(self):
        return len(self.sse_global_clients.keys())

    def connect(self, channel):
        """
        添加连接对象，请求建立sse连接时调用
        :param channel: 连接id
        """
        if not channel:
            return False

        if len(self.sse_global_clients) > self.max_connect_count:
            return False

        channel = str(channel)

        self.sse_global_clients.setdefault(channel, {
            self.Field.MESSAGE_LIST: [],
            self.Field.CONNECT_TIME: datetime.now()
        })

        return True

    def get_sse(self, channel):
        """
        获取连接对象
        :param channel: 连接id
        """
        sse_connect = self.sse_global_clients.get(channel)
        if not sse_connect:
            return {
                self.Field.MESSAGE_LIST: [],
                self.Field.CONNECT_TIME: datetime.now()
            }

        return sse_connect

    def del_sse(self, channel):
        """
        删除连接对象
        :param channel: 连接id
        """
        if channel in self.sse_global_clients:
            del self.sse_global_clients[channel]

    def add_message(self, channel, message):
        """
        添加消息到连接对象，监听到redis-pub-sub消息时调用
        :param channel: 连接id
        :param message: 消息
        """
        sse_connect = self.get_sse(channel)
        message_list = sse_connect.get(self.Field.MESSAGE_LIST, [])
        message_list.append(message)
        sse_connect.update({
            self.Field.MESSAGE_LIST: message_list,
        })

        self.sse_global_clients.setdefault(channel, sse_connect)

    def listen_message(self, channel):
        """
        监听消息
        """
        sse_connect = self.get_sse(channel)
        message_list = sse_connect.get(self.Field.MESSAGE_LIST, [])
        connect_time = sse_connect.get(self.Field.CONNECT_TIME, datetime.now())

        # 最大超时范围内，轮训消息
        while (datetime.now() - connect_time).seconds < self.max_connect_time:
            if not message_list:
                time.sleep(self.listen_interval)
                continue

            message = message_list.pop(0)
            if not message:
                time.sleep(self.listen_interval)
                continue

            yield message
            time.sleep(self.listen_interval)

        # 超时，断开连接
        print({
            'title': '连接超时，断开连接',
            'channel': channel,
            'channel_count': len(self.sse_global_clients.keys())
        })
        self.del_sse(channel)
        yield None


# 全局sse连接对象
sse_clients_global = SseClientsGlobal()
