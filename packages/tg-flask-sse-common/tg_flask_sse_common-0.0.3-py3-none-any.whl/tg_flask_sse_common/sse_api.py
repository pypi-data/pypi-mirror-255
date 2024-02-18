#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    stream.py
    ~~~~~~~~~~~~~~~~~~~~~~~

    处理sse连接接口

    :author: Tangshimin
    :copyright: (c) 2024,
    :date created: 2024-01-29

"""
import json
from .sse_core import Sse
from .sse_event_message import SseEventType


def sse_stream_connect_channel():
    """
    ## 获取当前连接订阅sse的频道号

    Returns:
    * `channel` (str) 当前连接订阅sse的频道号
    ---
    """
    return True, Sse.get_channel(), 200


def sse_stream_connect(channel, extra=None):
    """
    ## 订阅sse频道消息

    Params:
    * `channel` (str) 请求连接订阅通道
    * `extra` (str) 额外参数

    Returns:
    * `event` (str) 消息类型
    * `id` (str) 消息id
    * `data` (str) 消息内容
    * `retry` (int) 重试时间
    * `channel` (str) 订阅通道
    ---
    """

    if not channel:
        return False, "channel is require", 400

    try:
        if extra:
            extra = json.loads(extra)
    except:
        extra = {}

    is_connect = Sse.connect(channel=channel)

    if not is_connect:
        return False, "connect failed, connect limit", 400

    def default_generator():
        for message in Sse.subscribe_message(channel, extra):
            if not message:
                continue
            yield message.to_rsp_str()

    return default_generator()


def send_end_message(channel, data, _id):
    """
    ## 主动发送sse-end消息

    Params:
    * `channel` (str) 订阅通道
    * `id` (str) 消息id
    * `data` (str) 消息内容
    * `retry` (int) 重试时间
    * `channel` (str) 订阅通道

    Returns:
    ---
    """
    if channel is None:
        return False, "channel is empty", 400

    if data is None:
        return False, "data is empty", 400

    if _id is None:
        return False, "id is empty", 400

    Sse.publish_message(channel=channel, data=data, event=SseEventType.END, _id=_id)

    return True, "ok", 200


def send_message(channel, data, _id):
    """
    ## 主动发送sse-message消息

    Params:
    * `channel` (str) 订阅通道
    * `id` (str) 消息id
    * `data` (str) 消息内容
    * `retry` (int) 重试时间
    * `channel` (str) 订阅通道

    Returns:
    ---
    """
    if channel is None:
        return False, "channel is empty", 400

    if data is None:
        return False, "data is empty", 400

    if _id is None:
        return False, "id is empty", 400

    Sse.publish_message(data=data, event=SseEventType.MESSAGE, _id=_id, channel=channel)

    return True, "ok", 200

