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
import json
from datetime import datetime
import traceback
import time
from bson import ObjectId

from .sse_cache import SseNodeConnectStatsCache, SseEventMessageCache
from .sse_constant import RedisPubSubField
from .sse_event_message import ERROR_MESSAGE, END_MESSAGE, REDIS_MESSAGE
from .sse_message import SseMessage, SseMessageField
from .sse_event_message import SseEventType
from .sse_constant import RedisPubSubConfig


class SseRedisPubSub(object):
    """
    全局redis-pub-sub对象
    """
    def __init__(self, redis_client, key_prefix, sse_clients):
        self.redis = redis_client
        self.redis_pubsub = redis_client.pubsub()
        self.sse_node_connect_stats_cache = SseNodeConnectStatsCache(redis_client, key_prefix)
        self.sse_event_message_cache = SseEventMessageCache(redis_client, key_prefix)
        self.listen_interval = RedisPubSubConfig.LISTEN_INTERVAL
        self.sse_clients = sse_clients

    def listen(self):
        """
        监听redis订阅频道，将收到的消息推送到全局sse连接对象
        """
        channel = ''
        try:
            print({
                'title': '开启监听redis频道',
                'channel_count': self.sse_clients.count()
            })
            while True:
                sub_message = self.redis_pubsub.get_message(timeout=1)
                if not sub_message:
                    time.sleep(self.listen_interval)
                    continue

                channel, message, brk = self.sse_event_message_handler(sub_message)
                if not message:
                    time.sleep(self.listen_interval)
                    continue

                self.sse_event_message_cache.add_sub_message({
                    'channel': channel,
                    'message': message.to_dict(),
                    'time': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                })

                # 消息推送到全局sse连接对象
                if not self.is_system_message(message):
                    self.sse_clients.add_message(channel, message)

                if brk:
                    self.disconnect(channel)
                    break

                time.sleep(self.listen_interval)

        except:
            print({
                'title': '监听redis频道异常',
                'channel': channel,
                'exp': traceback.format_exc(),
                'channel_count': self.sse_clients.count()
            })
            pass

    def get_channel(self):
        """
        获取当前连接订阅sse的频道号
        """
        channel = str(ObjectId())
        info = self.sse_node_connect_stats_cache.get(channel)
        if info:
            return channel + datetime.now().strftime('%Y%m%d%H%M%S')
        return channel

    def subscribe(self, channel, extra=None):
        """
        订阅sse消息
        """
        self.redis_pubsub.subscribe(channel)

        self.sse_node_connect_stats_cache.add(channel, {
            'connect_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'extra': extra,
        })

        print({
            'title': '订阅成功',
            'channel': channel,
            'channel_count': self.sse_clients.count()
        })

    def publish_message(self, channel, data, event=None, _id=None, retry=None):
        """
        推送sse消息, 添加信息到redis发布队列记录
        """
        message = SseMessage(
            channel=channel, data=data, event=event, _id=_id, retry=retry
        ).to_dict()
        push_count = self.redis.publish(channel=channel, message=json.dumps(message))

        self.sse_event_message_cache.add_pub_message({
            'channel': channel,
            'message': message,
            'push_count': push_count > 0,
            'time': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        })

        if push_count > 0:
            print({
                'title': '消息推送成功',
                'channel': channel,
                'push_count': push_count,
                'channel_count': self.sse_clients.count()
            })
        else:
            print({
                'title': '消息推送失败，频道不存在',
                'channel': channel,
                'channel_count': self.sse_clients.count()
            })

        return push_count

    def disconnect(self, channel):
        """
        断开sse连接, 清理redis订阅连接缓存
        """
        print({
            'title': '取消订阅',
            'channel': channel,
            'channel_count': self.sse_clients.count()
        })
        # 取消订阅
        self.redis_pubsub.unsubscribe(channel)
        # 清理连接缓存
        self.sse_node_connect_stats_cache.delete(channel)
        # 删除全局连接对象
        self.sse_clients.del_sse(channel)

    @staticmethod
    def is_system_message(message):
        """
        是否是系统消息
        """
        if not message:
            return True
        if not isinstance(message, SseMessage):
            return True
        event = message.to_dict().get(SseMessageField.EVENT, '')
        return event in [
            SseEventType.END, SseEventType.ERROR, SseEventType.REDIS,
        ]

    @staticmethod
    def sse_event_message_handler(sub_message):
        """
        sse消息类型处理
        :param sub_message: redis订阅消息

        :return:
            message: sse消息
            brk: 是否中断结束
        """
        try:
            if not sub_message:
                return SseEventType.ERROR, ERROR_MESSAGE, False

            # 需要先解码
            for key, value in sub_message.items():
                if isinstance(key, bytes):
                    key = key.decode('utf-8')
                if isinstance(value, bytes):
                    value = value.decode('utf-8')
                sub_message[key] = value

            channel = sub_message.get(SseMessageField.CHANNEL)
            if not channel:
                return SseEventType.ERROR, ERROR_MESSAGE, False

            # 非message类型不处理
            if sub_message[RedisPubSubField.TYPE] != RedisPubSubField.Type.MESSAGE:
                return SseEventType.REDIS, REDIS_MESSAGE, False

            sub_message_data = sub_message.get(RedisPubSubField.DATA, '')
            if not sub_message_data:
                return SseEventType.ERROR, ERROR_MESSAGE, False

            # 主动结束消息
            sse_message = json.loads(sub_message_data)
            if sse_message.get(SseMessageField.EVENT) == SseEventType.END:
                return channel, END_MESSAGE, True

            # 普通消息
            message = SseMessage(
                channel=sse_message.get(SseMessageField.CHANNEL),
                data=sse_message.get(SseMessageField.DATA),
                event=sse_message.get(SseMessageField.EVENT),
                _id=sse_message.get(SseMessageField.ID),
                retry=sse_message.get(SseMessageField.RETRY)
            )

            return channel, message, False
        except:
            return SseEventType.ERROR, ERROR_MESSAGE, False


