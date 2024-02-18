#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    sse_event_message.py
    ~~~~~~~~~~~~~~~~~~~~~~~

    sse内置消息定义

    :author: Tangshimin
    :copyright: (c) 2024, Tungee
    :date created: 2024-01-29

"""
from datetime import datetime

from .sse_message import SseMessage
from .sse_constant import SseClientConfig


class SseEventType(object):
    """
    sse消息类型定义
    """
    END = "END"
    MESSAGE = "MESSAGE"
    ERROR = "ERROR"
    REDIS = "REDIS"


# redis消息
REDIS_MESSAGE = SseMessage(
    channel=SseEventType.REDIS,
    data=SseEventType.REDIS,
    event=SseEventType.REDIS,
    _id=str(int(datetime.now().timestamp() * 1000000)),
    retry=SseClientConfig.MAX_CONNECT_TIME * 1000
)

# error消息
ERROR_MESSAGE = SseMessage(
    channel=SseEventType.ERROR,
    data=SseEventType.ERROR,
    event=SseEventType.ERROR,
    _id=str(int(datetime.now().timestamp() * 1000000)),
    retry=SseClientConfig.MAX_CONNECT_TIME * 1000
)

# end消息
END_MESSAGE = SseMessage(
    channel=SseEventType.END,
    data=SseEventType.END,
    event=SseEventType.END,
    _id=str(int(datetime.now().timestamp() * 1000000)),
    retry=SseClientConfig.MAX_CONNECT_TIME * 1000
)
