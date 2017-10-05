import asyncio
from unittest import mock

import pytest

pytestmark = pytest.mark.asyncio


async def test_emit_full_queue(setup_logger, loop, mocker):
    log, hdlr, srv = await setup_logger(qsize=1, close_timeout=0.01)

    fut = asyncio.Future(loop=loop)

    async def coro(record):
        await fut

    hdlr._send = coro
    m_log = mocker.patch('aiologstash.base_handler.logger')

    log.info('Msg 1')
    assert not m_log.called
    log.info('Msg 2')
    m_log.warning.assert_called_with(
        'Queue is full, drop oldest message: "%(record)s"',
        {'record': mock.ANY})


async def test_emit_unexpected_err_in_worker(setup_logger, loop, mocker):
    log, hdlr, srv = await setup_logger()

    err = RuntimeError()
    fut = asyncio.Future(loop=loop)

    async def coro(record):
        fut.set_result(None)
        raise err

    hdlr._send = coro
    m_log = mocker.patch('aiologstash.base_handler.logger')

    log.info('Msg')
    await fut
    m_log.warning.assert_called_with('Unexpected Exception while sending log',
                                     exc_info=err)
