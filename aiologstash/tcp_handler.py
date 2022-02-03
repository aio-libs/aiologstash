import asyncio
from typing import Any, Mapping, Optional

from .base_handler import BaseLogstashHandler


class TCPLogstashHandler(BaseLogstashHandler):
    def __init__(
        self,
        *,
        host: str,
        port: int,
        level: int,
        close_timeout: float,
        qsize: int,
        loop: asyncio.AbstractEventLoop,
        reconnect_delay: float,
        reconnect_jitter: float,
        extra: Mapping[str, Any],
        **kwargs: Any
    ) -> None:
        super().__init__(
            level=level,
            close_timeout=close_timeout,
            qsize=qsize,
            reconnect_delay=reconnect_delay,
            reconnect_jitter=reconnect_jitter,
            extra=extra,
            loop=loop,
        )
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._host = host
        self._port = port
        self._kwargs = kwargs

    async def _connect(self) -> None:
        self._reader, self._writer = await asyncio.open_connection(
            self._host, self._port, **self._kwargs
        )

    async def _send(self, data: bytes) -> None:
        assert self._writer is not None
        self._writer.write(data)
        await self._writer.drain()

    async def _disconnect(self) -> None:
        if self._writer is not None:
            self._writer.close()
            await asyncio.sleep(0)  # wait for writer closing
            self._reader = None
            self._writer = None
