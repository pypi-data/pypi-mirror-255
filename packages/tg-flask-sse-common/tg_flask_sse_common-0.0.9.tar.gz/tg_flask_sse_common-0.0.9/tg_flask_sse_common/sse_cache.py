#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    sse_cache.py
    ~~~~~~~~~~~~~~~~~~~~~~~

    sse消息推送和订阅

    :author: Tangshimin
    :copyright: (c) 2024, Tungee
    :date created: 2024-01-29

"""
import json
from datetime import datetime


class SseConnectStatsCache(object):
    """
    节点sse连接状态信息统计缓存
    用于统计每个节点下的所有channel-sse连接状态信息，用于查看节点下所有用户的连接状态
    info : {
        'channel': '122121',
        'connect_time': '2024-01-29 12:00:00',
        'extra': {},
    }
    """
    def __init__(self, redis_client, key_prefix):
        self.redis = redis_client
        self.tail = datetime.now().strftime('%Y%m%d%H')
        self.prefix = key_prefix + ':sse:'
        self.expire = 60 * 60 * 12

    def key(self):
        return self.prefix + 'connect_stats_info:' + self.tail

    def add(self, channel, info):
        info = json.dumps(info)
        self.redis.hset(self.key(), channel, info)
        self.redis.expire(self.key(), self.expire)

    def get(self, channel):
        data = self.redis.hget(self.key(), channel)
        if data is None:
            return {}

        if isinstance(data, bytes):
            data = data.decode('utf-8')

        return json.loads(data)

    def get_all(self):
        datas = self.redis.hgetall(self.key())
        if datas is None:
            return {}

        for key, value in datas.items():
            if isinstance(key, bytes):
                key = key.decode('utf-8')
            if isinstance(value, bytes):
                datas[key] = json.loads(value.decode('utf-8'))

        return datas

    def delete(self, channel):
        self.redis.hdel(self.key(), channel)


class SseEventMessageCache(object):
    """
    sse消息缓存
    """
    def __init__(self, redis_client, key_prefix):
        self.redis = redis_client
        self.tail = datetime.now().strftime('%Y%m%d%H')
        self.prefix = key_prefix + ':sse:'
        self.expire = 60 * 60 * 12

    def pub_key(self):
        return self.prefix + 'pub_event_message:' + self.tail

    def sub_key(self):
        return self.prefix + 'sub_event_message:' + self.tail

    def add_pub_message(self, message):
        message = json.dumps(message)
        self.redis.lpush(self.pub_key(), message)
        self.redis.expire(self.pub_key(), self.expire)

    def add_sub_message(self, message):
        message = json.dumps(message)
        self.redis.lpush(self.sub_key(), message)
        self.redis.expire(self.sub_key(), self.expire)

    def get_pub_all(self):
        message = self.redis.lrange(self.pub_key(), 0, -1)
        if message is None:
            return []

        for i in range(len(message)):
            if isinstance(message[i], bytes):
                message[i] = json.loads(message[i].decode('utf-8'))

        return message

    def get_sub_all(self):
        message = self.redis.lrange(self.sub_key(), 0, -1)
        if message is None:
            return []

        for i in range(len(message)):
            if isinstance(message[i], bytes):
                message[i] = json.loads(message[i].decode('utf-8'))

        return message
