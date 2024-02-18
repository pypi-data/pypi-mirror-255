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
import redis

from .sse_constant import RedisConfig
from .sse_clients_global import sse_clients_global
from .sse_redis_pub_sub import SseRedisPubSub


class Sse(object):
    def __init__(self, redis_config):
        host = redis_config['host'] or RedisConfig.HOST
        port = redis_config['port'] or RedisConfig.PORT
        password = redis_config['password'] or RedisConfig.PASSWORD
        db = redis_config['db'] or RedisConfig.DB
        key_prefix = redis_config['key_prefix'] or RedisConfig.KEY_PREFIX

        redis_client = redis.StrictRedis(
            host=host, port=port,
            password=password, db=db,
        )

        self.redis_client = redis_client

        self.sse_redis_pub_sub = SseRedisPubSub(
            redis_client=redis_client, key_prefix=key_prefix
        )

    def get_channel(self):
        """
        获取当前连接订阅sse的频道号
        """
        return self.sse_redis_pub_sub.get_channel()

    @staticmethod
    def connect(channel):
        """
        添加连接对象
        :param channel: 连接id
        """
        return sse_clients_global.connect(channel)

    def listen(self):
        if not sse_clients_global.is_running:
            sse_clients_global.is_running = True
            self.sse_redis_pub_sub.listen()

    def subscribe_message(self, channel, extra=None):
        """
        订阅sse消息, 添加信息到redis订阅频道
        """
        self.sse_redis_pub_sub.subscribe(
            channel=channel,
            extra=extra
        )

        return sse_clients_global.listen_message(channel)

    def publish_message(self, channel, data, event=None, _id=None, retry=None):
        """
        推送sse消息, 添加信息到redis发布队列记录
        """
        return self.sse_redis_pub_sub.publish_message(
            channel=channel,
            data=data,
            event=event,
            _id=_id,
            retry=retry
        )

    def heartbeat(self):
        """
        心跳
        """
        return self.sse_redis_pub_sub.send_sse_heartbeat()

    @staticmethod
    def sse_run():
        thread = threading.Thread(target=Sse.listen)
        thread.start()
