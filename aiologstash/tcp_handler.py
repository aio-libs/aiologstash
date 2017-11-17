import asyncio

from .base_handler import BaseLogstashHandler


class TCPLogstashHandler(BaseLogstashHandler):

    def __init__(self, *, host, port,
                 level, close_timeout, qsize, loop,
                 reconnect_delay, reconnect_jitter,
                 extra,
                 **kwargs):
        super().__init__(level=level,
                         close_timeout=close_timeout, qsize=qsize,
                         reconnect_delay=reconnect_delay,
                         reconnect_jitter=reconnect_jitter,
                         extra=extra,
                         loop=loop)
        self._reader = None
        self._writer = None
        self._host = host
        self._port = port
        self._kwargs = kwargs

    async def _connect(self):
        self._reader, self._writer = await asyncio.open_connection(
            self._host, self._port,
            loop=self._loop,
            **self._kwargs)

    async def _send(self, data):
        self._writer.write(data)
        await self._writer.drain()

    async def _disconnect(self):
        if self._writer is not None:
            self._writer.close()
            await asyncio.sleep(0, loop=self._loop)  # wait for writer closing
            self._reader = None
            self._writer = None
