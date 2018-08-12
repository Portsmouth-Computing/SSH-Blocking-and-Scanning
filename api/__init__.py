# -*- coding: utf-8 -*-

"""
MIT License

Copyright (c) 2018 Samuel Riches

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import asyncio
import signal

import aiohttp
import asyncpg
import sanic

from .config import Config
from .routes import bp as api_routes


class Server:
    def __init__(self, config, *, loop=None):
        self.app = app = sanic.Sanic(configure_logging=False)
        self.config = app.cfg = config

        self.loop = loop = loop or asyncio.get_event_loop()

        self.db = app.db = None
        self.session = app.session = aiohttp.ClientSession(loop=loop)

        app.config['LOGO'] = None

        app.blueprint(api_routes)
        app.add_route(self.root, '/', methods=['GET', 'HEAD'])

    @classmethod
    def with_config(cls, path='config.yaml', *, loop=None):
        return cls(Config.from_file(path), loop=loop)

    async def start(self, *args, **kwargs):
        self.db = self.app.db = await asyncpg.create_pool(**self.config.postgres)

        await self.app.create_server(*args, **kwargs)

    def run(self, *args, host='0.0.0.0', port=8000, **kwargs):
        for sig in (signal.SIGINT, signal.SIGTERM):
            self.loop.add_signal_handler(sig, self.loop.stop)

        self.loop.run_until_complete(self.start(*args, host=host, port=port, **kwargs))

        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            self.loop.stop()

    async def root(self, request):
        return sanic.response.text('There is no 127.0.0.1 for you. Please refer to the docs for the endpoints')
