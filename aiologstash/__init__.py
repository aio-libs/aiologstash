"""asyncio-compatible logstash logging handler."""


__version__ = '0.0.3'

import asyncio
import logging

from .tcp_handler import TCPLogstashHandler


__all__ = ('create_tcp_handler',)


async def create_tcp_handler(host, port,
                             level=logging.NOTSET, close_timeout=5,
                             reconnect_delay=1, reconnect_jitter=0.3,
                             qsize=10000, loop=None, **kwargs):
    if loop is None:
        loop = asyncio.get_event_loop()
    handler = TCPLogstashHandler(host=host, port=port,
                                 level=level,
                                 close_timeout=close_timeout,
                                 qsize=qsize, loop=loop,
                                 reconnect_delay=reconnect_delay,
                                 reconnect_jitter=reconnect_jitter,
                                 **kwargs)
    try:
        await handler._connect()
    except OSError:
        handler.close()
        await handler.wait_closed()
        raise
    return handler
