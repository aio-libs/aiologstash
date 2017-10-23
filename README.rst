aiologstash
===========

.. image:: https://travis-ci.org/wikibusiness/aiologstash.svg?branch=master
  :target:  https://travis-ci.org/wikibusiness/aiologstash

.. image:: https://codecov.io/gh/wikibusiness/aiologstash/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/wikibusiness/aiologstash

.. image:: https://badge.fury.io/py/aiologstash.svg
  :target: https://badge.fury.io/py/aiologstash

asyncio logging handler for logstash.

Installation
------------

.. code-block:: shell

   pip install aiologstash

Usage
-----

.. code-block:: python

   import logging
   from aiologstash import create_tcp_handler

   async def init_logger():
        handler = await create_tcp_handler('127.0.0.1', 5000)
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        root.addHandler(handler)
