import asyncio

from .base_handler import BaseLogstashHandler


class TCPLogstashHandler(BaseLogstashHandler):

    def __init__(self, host, port,
                 formatter, level, close_timeout, qsize, loop,
                 **kwargs):
        super().__init__(formatter, level, close_timeout, qsize, loop,
                         **kwargs)
        self._reader = None
        self._writer = None
        self._host = host
        self._port = port

    async def connect(self):
        self._reader, self._writer = await asyncio.open_connection(
            self._host, self._port,
            loop=self._loop)

    async def _send(self, record):
        data = self._serialize(record)
        self._writer.write(data)
        await self._writer.drain()

    async def wait_closed(self):
        await super().wait_closed()
        self._writer.close()
        await asyncio.sleep(0, loop=self._loop)  # wait for writer closing
