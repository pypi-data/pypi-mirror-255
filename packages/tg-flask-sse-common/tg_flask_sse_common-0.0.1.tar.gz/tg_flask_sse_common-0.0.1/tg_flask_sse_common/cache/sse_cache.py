#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    sse_cache.py
    ~~~~~~~~~~~~~~~~~~~~~~~

    sse消息推送和订阅

    :author: Tangshimin
    :copyright: (c) 2024, 
    :date created: 2024-01-29

"""
import redis
import json
from datetime import datetime

from configs.constant import RedisConfig

redis_client = redis.StrictRedis(
    host=RedisConfig.HOST,
    port=RedisConfig.PORT,
    password=RedisConfig.PASSWORD,
    db=RedisConfig.DB,
)


class SseNodeConnectStatsCache(object):
    """
    节点sse连接状态信息统计缓存
    用于统计每个节点下的所有channel-sse连接状态信息，用于查看节点下所有用户的连接状态
    info : {
        'connect_time': 'connect_time',
        'data': 'data',
    }
    """
    def __init__(self):
        self.redis = redis_client
        self.tail = datetime.now().strftime('%Y%m%d')
        self.prefix = RedisConfig.KEY_PREFIX + ':sse:'

    def key(self):
        return self.prefix + 'node_connect_stats_info:' + self.tail

    def add(self, channel, info):
        info = json.dumps(info)
        self.redis.hset(self.key(), channel, info)

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
    def __init__(self):
        self.redis = redis_client
        self.tail = datetime.now().strftime('%Y%m%d')
        self.prefix = RedisConfig.KEY_PREFIX + ':sse:'

    def pub_key(self):
        return self.prefix + 'pub_event_message:' + self.tail

    def sub_key(self):
        return self.prefix + 'sub_event_message:' + self.tail

    def add_pub_message(self, message):
        message = json.dumps(message)
        self.redis.lpush(self.pub_key(), message)

    def add_sub_message(self, message):
        message = json.dumps(message)
        self.redis.lpush(self.sub_key(), message)

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
