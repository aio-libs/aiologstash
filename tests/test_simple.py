import socket
from unittest import mock

import pytest

from aiologstash import create_tcp_handler

pytestmark = pytest.mark.asyncio


async def test_simple(setup_logger, loop):
    log, srv = await setup_logger()
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
