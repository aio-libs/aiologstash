"""asyncio-compatible logstash logging handler."""


__version__ = '0.0.1a0'

import logging

from .tcp_handler import TCPLogstashHandler


__all__ = ('create_tcp_handler',)


async def create_tcp_handler(host, port, formatter=None,
                             level=logging.NOTSET, close_timeout=5,
                             qsize=10000, **kwargs):
    handler = TCPLogstashHandler(host=host, port=port,
                                 formatter=formatter, level=level,
                                 close_timeout=close_timeout,
                                 qsize=qsize, **kwargs)
    await handler.connect()
    return handler
