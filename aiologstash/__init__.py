"""asyncio-compatible logstash logging handler."""


__version__ = '0.0.3a0'

import asyncio
import logging

from .tcp_handler import TCPLogstashHandler


__all__ = ('create_tcp_handler',)


async def create_tcp_handler(host, port, formatter=None,
                             level=logging.NOTSET, close_timeout=5,
                             qsize=10000, loop=None, **kwargs):
    if loop is None:
        loop = asyncio.get_event_loop()
    handler = TCPLogstashHandler(host=host, port=port,
                                 formatter=formatter, level=level,
                                 close_timeout=close_timeout,
                                 qsize=qsize, loop=loop, **kwargs)
    try:
        await handler.connect()
    except OSError:
        handler.close()
        await handler.wait_closed()
        raise
    return handler
