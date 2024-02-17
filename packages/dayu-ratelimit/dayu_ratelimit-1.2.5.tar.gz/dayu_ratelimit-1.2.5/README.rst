ratelimit
########


1. 安装
==========

.. code-block:: shell

   pip install ratelimit-py3

2. 示例
==========

- 2.1 异步

.. code-block:: python

    @AsyncRateLimit(limit=3)
    async def add(a, b):
        await asyncio.sleep(0.01)
        return a + b


    @AsyncRateLimit(limit=3, uniform_rate=True)
    async def sub(a, b):
        await asyncio.sleep(0.2)
        return a - b

- 2.2 同步

.. code-block:: python

    @RateLimit(limit=3)
    def add(a, b):
        time.sleep(0.01)
        return a + b


    @RateLimit(limit=3, uniform_rate=True)
    def sub(a, b):
        time.sleep(0.02)
        return a - b


