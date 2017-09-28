aiologstash
==============


asyncio logging handler for logstash.


Installation::

   $ pip install aiologstash


Usage::

   import logging
   from aiologstash import create_tcp_handler

   async def init_logger():
        handler = await create_tcp_handler('127.0.0.1', 5000)
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        root.addHandler(handler)
