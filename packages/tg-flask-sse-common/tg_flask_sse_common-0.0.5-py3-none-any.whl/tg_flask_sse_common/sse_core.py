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
from .sse_clients import SseClients
from .sse_redis_pub_sub import SseRedisPubSub


class Sse(object):
    def __init__(self, redis_config, sse_clients_config):
        host = redis_config['host'] or RedisConfig.HOST
        port = redis_config['port'] or RedisConfig.PORT
        password = redis_config['password'] or RedisConfig.PASSWORD
        db = redis_config['db'] or RedisConfig.DB
        key_prefix = redis_config['key_prefix'] or RedisConfig.KEY_PREFIX

        # 初始化redis连接
        redis_client = redis.StrictRedis(
            host=host, port=port,
            password=password, db=db,
        )
        self.redis_client = redis_client

        # 初始化sse连接对象
        sse_clients = SseClients(sse_clients_config)
        self.sse_clients = sse_clients

        # 初始化redis-pub-sub对象
        self.sse_redis_pub_sub = SseRedisPubSub(
            redis_client=redis_client, key_prefix=key_prefix,
            sse_clients=sse_clients
        )

    def get_channel(self):
        """
        获取当前连接订阅sse的频道号
        """
        return self.sse_redis_pub_sub.get_channel()

    def connect(self, channel):
        """
        添加连接对象
        :param channel: 连接id
        """
        return self.sse_clients.connect(channel)

    def listen(self):
        if not self.sse_clients.is_running:
            self.sse_clients.is_running = True
            self.sse_redis_pub_sub.listen()

    def subscribe_message(self, channel, extra=None):
        """
        订阅sse消息, 添加信息到redis订阅频道
        """
        self.sse_redis_pub_sub.subscribe(
            channel=channel,
            extra=extra
        )

        message_generator = self.sse_clients.listen_message(channel)
        if message_generator is None:
            self.sse_redis_pub_sub.disconnect(channel)
            return None

        return message_generator

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

    @staticmethod
    def sse_run():
        thread = threading.Thread(target=Sse.listen)
        thread.start()
