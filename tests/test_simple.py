import socket
from unittest import mock

import pytest

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
