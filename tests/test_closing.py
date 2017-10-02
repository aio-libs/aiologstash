from unittest import mock

import pytest

pytestmark = pytest.mark.asyncio


async def test_no_emit_on_closed(setup_logger, mocker):
    log, hdlr, srv = await setup_logger()
    hdlr.close()
    m_log = mocker.patch('aiologstash.base_handler.logger')
    log.info('Test')
    m_log.warning.assert_called_with(
        'Log message skipped due shutdown "%(record)s"',
        {'record': mock.ANY})


async def test_close_on_closed(setup_logger, mocker):
    log, hdlr, srv = await setup_logger()
    hdlr.close()
    hdlr.close()
    assert hdlr._closing
    assert hdlr._worker is not None



async def test_wait_closed_on_closed(setup_logger, mocker):
    log, hdlr, srv = await setup_logger()
    hdlr.close()
    await hdlr.wait_closed()
    await hdlr.wait_closed()
    assert hdlr._closing
    assert hdlr._worker is None
    assert hdlr._queue.qsize() == 0
