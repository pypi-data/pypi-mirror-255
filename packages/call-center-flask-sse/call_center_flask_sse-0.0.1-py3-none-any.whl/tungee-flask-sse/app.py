#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    app.py
    ~~~~~~~~~~~~~~~~~~~~~~~

    sse服务端推送启动模块

    :author: Tangshimin
    :copyright: (c) 2024, Tungee
    :date created: 2024-01-29

"""
from flask import Flask

from api import sse_api

app = Flask(__name__)


app.register_blueprint(sse_api, url_prefix='/internal-api')


