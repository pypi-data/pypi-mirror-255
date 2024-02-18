#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    sse_constant.py
    ~~~~~~~~~~~~~~~~~~~~~~~

    静态配置文件

    :author: Tangshimin
    :copyright: (c) 2024, Tungee
    :date created: 2024-01-29

"""


class RedisPubSubField(object):
    """
    redis pubsub消息字段
    """
    TYPE = 'type'
    DATA = 'data'
    PATTERN = 'pattern'

    class Type(object):
        """
        redis pubsub消息类型
        """
        MESSAGE = 'message'
        P_MESSAGE = 'pmessage'
        SUBSCRIBE = 'subscribe'
        UNSUBSCRIBE = 'unsubscribe'
        P_SUBSCRIBE = 'psubscribe'
        P_UNSUBSCRIBE = 'punsubscribe'


class SseMessageField(object):
    """
    sse消息字段
    """
    ID = "id"
    DATA = "data"
    EVENT = "event"
    RETRY = "retry"
    CHANNEL = 'channel'


class RedisConfig(object):
    HOST = '127.0.0.1'
    PORT = 6379
    DB = 0
    PASSWORD = ''
    KEY_PREFIX = 'call-center'


class SseClientConfig(object):
    # 连接最大时长
    MAX_CONNECT_TIME = 600
    # 单进程最大连接数
    MAX_CONNECT_COUNT = 2000
    # 连接监听消息-轮训时间间隔
    LISTEN_INTERVAL = 1


class RedisPubSubConfig(object):
    # pub-sub监听-轮训时间间隔
    LISTEN_INTERVAL = 0.05
