import asyncio
import gc
import logging
import sys

from json import loads

import pytest

from aiologstash import create_tcp_handler

asyncio.set_event_loop(None)


logging.getLogger().setLevel(logging.DEBUG)


if sys.version_info >= (3, 5, 2):
    def create_future(loop):
        return loop.create_future()
else:
    def create_future(loop):  # pragma: no cover
        """Compatibility wrapper for the loop.create_future() call introduced in
        3.5.2."""
        return asyncio.Future(loop=loop)


@pytest.fixture
def event_loop(request):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    yield loop

    if not loop.is_closed():
        loop.call_soon(loop.stop)
        loop.run_forever()
        loop.close()

    gc.collect()
    asyncio.set_event_loop(None)


@pytest.fixture
def loop(event_loop):
    return event_loop


class FakeTcpServer:
    def __init__(self, loop):
        self.loop = loop
        self.data = bytearray()
        self.server = None
        self.futs = set()

    async def start(self):
        self.server = await asyncio.start_server(self.on_connect,
                                                 host='127.0.0.1',
                                                 loop=self.loop)

    @property
    def port(self):
        return self.server.sockets[0].getsockname()[1]

    @property
    def jsons(self):
        s = self.data.decode('utf8')
        return [loads(i) for i in s.split('\n') if i]

    async def close(self):
        if self.server is None:
            return
        self.server.close()
        await self.server.wait_closed()
        self.server = None

    async def on_connect(self, reader, writer):
        while True:
            data = await reader.read(1024)
            if not data:
                break
            self.data.extend(data)
            for fut in self.futs:
                if not fut.done():
                    fut.set_result(None)

    async def wait(self):
        fut = create_future(self.loop)
        self.futs.add(fut)
        await fut
        self.futs.remove(fut)


@pytest.fixture
def make_tcp_server(loop):
    servers = []

    async def go():
        server = FakeTcpServer(loop)
        await server.start()
        servers.append(server)
        return server

    yield go

    async def finalize():
        for server in servers:
            await server.close()
    loop.run_until_complete(finalize())


@pytest.fixture
def make_tcp_handler(loop, make_tcp_server):
    handlers = []

    async def go(*args, level=logging.DEBUG, **kwargs):
        server = await make_tcp_server()
        handler = await create_tcp_handler('127.0.0.1', server.port,
                                           loop=loop, **kwargs)
        handlers.append(handler)
        return handler, server

    yield go

    async def finalize():
        for handler in handlers:
            handler.close()
            await handler.wait_closed()

    loop.run_until_complete(finalize())


@pytest.fixture
def setup_logger(make_tcp_handler):
    async def go(*args, **kwargs):
        handler, server = await make_tcp_handler(*args, **kwargs)
        logger = logging.getLogger('aiologstash_test')
        logger.addHandler(handler)
        return logger, handler, server
    yield go
