"""
MIT License

Copyright (c) 2018 SnowyLuma

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

import logging
import contextlib


# modules which have spammy or not useful logs on DEBUG
SILENCED_LOGGERS = ('discord', 'PIL', 'websockets')


def fix_logging():
    # as sanic requires a different log format for it's access log we have to do this little dance

    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s]: %(request)s %(status)d %(byte)d %(host)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    access = logging.getLogger('sanic.access')
    access.addHandler(handler)

    # normally loggers propagate to higher hierarchy loggers, but due to the change in format we have to disable this
    access.propagate = False


@contextlib.contextmanager
def setup_logging():
    """Context manager which sets up stdout logging and shuts down logging on block exit."""

    try:
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
        )

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        root.addHandler(handler)

        for name in SILENCED_LOGGERS:
            logging.getLogger(name).setLevel(logging.INFO)

        yield
    finally:
        logging.shutdown()
