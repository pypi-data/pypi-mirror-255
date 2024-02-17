import asyncio
import logging
import os
import sys
import time
from collections import deque
from functools import wraps

sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir))

from dayu.engines.timewindows import TimeWindowsRateLimitEngine, AsyncTimeWindowsRateLimitEngine
from dayu.engines.uniform import UniformRateLimitEngine, AsyncUniformRateLimitEngine
from dayu.utils import current

LOG = logging.getLogger(__name__)


class BaseRateLimit(object):
    def __init__(self, **kwargs):
        self._engine = None

    def __call__(self, func):
        func.limit = self
        if not self._engine:
            return func
        self._engine.set_func(func.__qualname__)


class RateLimit(BaseRateLimit):
    def __init__(self, limit=10, per=1, clock=current, wait=True, need_lock=True, enable=True, uniform_rate=False):
        super().__init__()
        if uniform_rate:
            self._engine = UniformRateLimitEngine(limit=limit, per=per, clock=clock, wait=wait, need_lock=need_lock)
        elif enable:
            self._engine = TimeWindowsRateLimitEngine(limit=limit, per=per, clock=clock, wait=wait, need_lock=need_lock, queue=deque())

    def __call__(self, func):
        super().__call__(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            self._engine.run_limit()
            return func(*args, **kwargs)

        return wrapper


class AsyncRateLimit(BaseRateLimit):
    def __init__(self, limit=10, per=1, clock=current, wait=True, enable=True, uniform_rate=False):
        super().__init__()
        if uniform_rate:
            self._engine = AsyncUniformRateLimitEngine(limit=limit, per=per, clock=clock, wait=wait)
        elif enable:
            self._engine = AsyncTimeWindowsRateLimitEngine(limit=limit, per=per, clock=clock, wait=wait, queue=deque())

    def __call__(self, func):
        super().__call__(func)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            await self._engine.run_limit()
            return await func(*args, **kwargs)

        return async_wrapper


