#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    run.py
    ~~~~~~~~~~~~~~~~~~~~~~~

    静态配置文件

    :author: Tangshimin
    :copyright: (c) 2024, Tungee
    :date created: 2024-01-29

"""
from gevent import monkey
# Monkey patch to support coroutine
# Must be at the start of the whole app
monkey.patch_all()

from app import app
from gevent.pywsgi import WSGIServer
from urllib.parse import unquote
from logic.sse_core import Sse


# 打印所有api
def print_rules():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():
        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)
        methods = ','.join(rule.methods)
        url = urllib.parse.unquote("{0}{1}".format(rule.rule, urllib.parse.urlencode(options)))
        line = urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
        output.append(line)

    for line in sorted(output):
        print(line)


print_rules()

Sse.sse_run()

print("server start")
http_server = WSGIServer(('127.0.0.1', 8888), app)
http_server.serve_forever()


