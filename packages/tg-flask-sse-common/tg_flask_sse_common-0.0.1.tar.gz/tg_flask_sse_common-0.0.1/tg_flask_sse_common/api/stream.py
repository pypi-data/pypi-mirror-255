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
import ujson
from flask import request, stream_with_context, Response, json as flask_json

from api import sse_api
from logic.sse_core import Sse
from logic.sse_event_message import SseEventType


@sse_api.route('/sse/stream/channel', methods=['GET'])
def sse_stream_connect_channel():
    """
    ## 获取当前连接订阅sse的频道号

        GET '/sse/stream/channel'

    Returns:
    * `channel` (str) 当前连接订阅sse的频道号
    ---
    """
    return jsonify(channel=Sse.get_channel()), 200


@sse_api.route('/sse/stream/connect')
def sse_stream_connect():
    """
    ## 订阅sse频道消息

        GET '/sse/stream/connect'

    Params:
    * `channel` (str) 请求连接订阅通道

    Returns:
    * `event` (str) 消息类型
    * `id` (str) 消息id
    * `data` (str) 消息内容
    * `retry` (int) 重试时间
    * `channel` (str) 订阅通道
    ---
    """
    channel = request.args.get('channel', '')
    extra = request.args.get('extra', '')

    if not channel:
        return jsonify(msg="channel is require"), 400

    try:
        if extra:
            extra = json.loads(extra)
    except:
        extra = {}

    is_connect = Sse.connect(channel=channel)

    if not is_connect:
        return jsonify(msg="connect failed, connect limit"), 400

    def default_generator():
        for message in Sse.subscribe_message(channel, extra):
            if not message:
                continue
            yield message.to_rsp_str()

    return Response(
        stream_with_context(default_generator()),
        mimetype="text/event-stream",
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
    )


@sse_api.route('/sse/send-message/end', methods=['GET'])
def send_end_message():
    """
    ## 主动发送sse-end消息

        GET '/sse/send-message/end'

    Params:
    * `channel` (str) 订阅通道
    * `id` (str) 消息id
    * `data` (str) 消息内容
    * `retry` (int) 重试时间
    * `channel` (str) 订阅通道

    Returns:
    ---
    """
    channel = request.args.get('channel')
    _id = request.args.get('id')
    data = request.args.get('data')

    if channel is None:
        return jsonify(msg='channel is empty'), 400

    if data is None:
        return jsonify(msg='data is empty'), 400

    if _id is None:
        return jsonify(msg='id is empty'), 400

    Sse.publish_message(channel=channel, data=data, event=SseEventType.END, _id=_id)

    return jsonify(msg='ok'), 200


@sse_api.route('/sse/send-message/message', methods=['GET'])
def send_message():
    """
    ## 主动发送sse-message消息

        GET '/sse/send-message/message'

    Params:
    * `channel` (str) 订阅通道
    * `id` (str) 消息id
    * `data` (str) 消息内容
    * `retry` (int) 重试时间
    * `channel` (str) 订阅通道

    Returns:
    ---
    """
    channel = request.args.get('channel')
    _id = request.args.get('id')
    data = request.args.get('data')

    if channel is None:
        return jsonify(msg='channel is empty'), 400

    if data is None:
        return jsonify(msg='data is empty'), 400

    if _id is None:
        return jsonify(msg='id is empty'), 400

    Sse.publish_message(data=data, event=SseEventType.MESSAGE, _id=_id, channel=channel)

    return jsonify(msg='ok'), 200


def jsonify(*args, **kwargs):
    """
    Create a JSON response with ujson
    """

    if args and kwargs:
        raise TypeError("jsonify() behavior undefined when passed both args and kwargs")

    elif len(args) == 1:  # single args are passed directly to dumps()
        data = args[0]
    else:
        data = args or kwargs

    try:
        dumped = ujson.dumps(data, ensure_ascii=False)
    except TypeError:
        dumped = flask_json.dumps(data, ensure_ascii=False)

    resp = Response(dumped, mimetype="application/json")

    return resp

