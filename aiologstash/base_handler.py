import abc
import asyncio
import logging
import random

from async_timeout import timeout
from logstash import LogstashFormatterVersion1

from .log import logger


class BaseLogstashHandler(logging.Handler):

    def __init__(self, *,
                 level, close_timeout, qsize, loop,
                 reconnect_delay, reconnect_jitter,
                 extra):
        self._close_timeout = close_timeout
        self._reconnect_delay = reconnect_delay
        self._reconnect_jitter = reconnect_jitter
        self._random = random.Random()
        self._extra = extra

        self._loop = loop

        self._queue = asyncio.Queue(maxsize=qsize, loop=self._loop)

        super().__init__(level=level)

        formatter = LogstashFormatterVersion1()
        self.setFormatter(formatter)

        self._closing = False
        self._worker = self._loop.create_task(self._work())

    @abc.abstractmethod
    async def _connect(self):
        pass  # pragma: no cover

    @abc.abstractmethod
    async def _send(self, data):
        pass  # pragma: no cover

    @abc.abstractmethod
    async def _disconnect(self):
        pass  # pragma: no cover

    def emit(self, record):
        if self._closing:
            msg = 'Log message skipped due shutdown "%(record)s"'
            context = {'record': record}
            logger.warning(msg, context)
            return

        if self._queue.full():
            msg = 'Queue is full, drop oldest message: "%(record)s"'
            context = {'record': self._queue.get_nowait()}
            logger.warning(msg, context)

        self._queue.put_nowait(record)

    async def _work(self):
        reconnection = False
        while True:
            if not reconnection:
                record = await self._queue.get()

            if record is ...:
                self._queue.put_nowait(...)
                break

            reconnection = False
            try:
                data = self._serialize(record)
                try:
                    await self._send(data)
                except (OSError, RuntimeError):
                    reconnection = True
                    await self._reconnect()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                msg = 'Unexpected exception while sending log'
                logger.warning(msg, exc_info=exc)

    async def _reconnect(self):
        logger.info('Transport disconnected')
        await self._disconnect()
        while True:
            try:
                await self._connect()
                logger.info('Transport reconnected')
                return
            except (OSError, RuntimeError):
                delay = self._random.gauss(self._reconnect_delay,
                                           self._reconnect_jitter)
                await asyncio.sleep(delay, loop=self._loop)

    def _serialize(self, record):
        for key, value in self._extra.items():
            if not hasattr(record, key):
                setattr(record, key, value)
        return self.format(record) + b'\n'

    # dummy statement for default handler close()
    # non conditional close() usage actually
    def close(self):
        if self._closing:
            return
        self._closing = True

        if self._queue.full():
            msg = ('Queue is full, drop oldest message before closing'
                   ': "%(record)s"')
            context = {'record': self._queue.get_nowait()}
            logger.warning(msg, context)
        self._queue.put_nowait(...)

        super().close()

    @abc.abstractmethod
    async def wait_closed(self):
        if self._worker is None:
            return  # already closed
        try:
            async with timeout(self._close_timeout, loop=self._loop):
                await self._worker
        except asyncio.TimeoutError:
            self._worker.cancel()

            try:
                await self._worker
            except:  # noqa
                pass

        self._worker = None

        assert self._queue.qsize() == 1
        assert self._queue.get_nowait() is ...
        await self._disconnect()
