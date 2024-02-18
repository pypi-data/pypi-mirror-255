#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    sse_message.py
    ~~~~~~~~~~~~~~~~~~~~~~~

    sse消息格式定义

    :author: Tangshimin
    :copyright: (c) 2024, Tungee
    :date created: 2024-01-29

"""
import json

from configs.constant import SseMessageField


class SseMessage(object):
    def __init__(self, channel, data, event=None, _id=None, retry=None):
        self.channel = channel
        self.data = data
        self.event = event
        self.id = _id
        self.retry = retry

    def to_dict(self):
        result = {
            SseMessageField.DATA: self.data,
            SseMessageField.CHANNEL: self.channel
        }
        if self.event:
            result[SseMessageField.EVENT] = self.event
        if self.id:
            result[SseMessageField.ID] = self.id
        if self.retry:
            result[SseMessageField.RETRY] = self.retry
        return result

    def to_rsp_str(self):
        if isinstance(self.data, str):
            data = self.data
        else:
            data = json.dumps(self.data)
        lines = ["%s:%s" % (SseMessageField.DATA, line) for line in data.splitlines()]
        if self.event:
            lines.insert(0, "%s:%s" % (SseMessageField.EVENT, self.event))
        if self.id:
            lines.append("%s:%s" % (SseMessageField.ID, self.id))
        if self.retry:
            lines.append("%s:%s" % (SseMessageField.RETRY, self.retry))
        if self.channel:
            lines.append("%s:%s" % (SseMessageField.CHANNEL, self.channel))
        return "\n".join(lines) + "\n\n"


