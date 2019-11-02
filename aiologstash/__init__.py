"""asyncio-compatible logstash logging handler."""


__version__ = "2.0.0"

import asyncio
import logging
import types
from typing import Any, Mapping

from .tcp_handler import TCPLogstashHandler


__all__ = ("create_tcp_handler",)


async def create_tcp_handler(
    host: str,
    port: int,
    level: int = logging.NOTSET,
    close_timeout: float = 5,
    reconnect_delay: float = 1,
    reconnect_jitter: float = 0.3,
    qsize: int = 10000,
    extra: Mapping[str, Any] = types.MappingProxyType({}),
    **kwargs: Any
) -> logging.Handler:
    loop = asyncio.get_event_loop()
    extra = types.MappingProxyType(extra)
    handler = TCPLogstashHandler(
        host=host,
        port=port,
        level=level,
        close_timeout=close_timeout,
        qsize=qsize,
        loop=loop,
        reconnect_delay=reconnect_delay,
        reconnect_jitter=reconnect_jitter,
        extra=extra,
        **kwargs
    )
    try:
        await handler._connect()
    except OSError:
        handler.close()
        await handler.wait_closed()
        raise
    return handler
