import socket
from unittest import mock

import pytest

from aiologstash import create_tcp_handler

pytestmark = pytest.mark.asyncio


async def test_simple(setup_logger, loop):
    log, hdlr, srv = await setup_logger()
    log.info('Info %s', 'text')
    await srv.wait()
    js = srv.jsons
    assert js[0] == {
        "@timestamp": mock.ANY,
        "@version": "1",
        "message": "Info text",
        "host": socket.gethostname(),
        "path": __file__,
        "tags": [],
        "type": "Logstash",
        "level": "INFO",
        "logger_name": "aiologstash_test",
        "stack_info": None}


async def test_cannot_connect(unused_tcp_port, loop):
    with pytest.raises(OSError):
        await create_tcp_handler('127.0.0.1', unused_tcp_port, loop=loop)


async def test_implicit_loop(make_tcp_server, loop):
    server = await make_tcp_server()
    handler = await create_tcp_handler('127.0.0.1', server.port)
    assert handler._loop is loop
    handler.close()
    await handler.wait_closed()


async def test_extra(setup_logger, loop):
    log, hdlr, srv = await setup_logger(extra={'app': 'myapp'})
    log.info('Info %s', 'text')
    await srv.wait()
    js = srv.jsons
    assert js[0] == {
        "@timestamp": mock.ANY,
        "@version": "1",
        "message": "Info text",
        "host": socket.gethostname(),
        "path": __file__,
        "tags": [],
        "type": "Logstash",
        "level": "INFO",
        "logger_name": "aiologstash_test",
        "stack_info": None,
        "app": "myapp"}
