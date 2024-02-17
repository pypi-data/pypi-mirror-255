import asyncio
import logging

from dayu.cores.engine import BaseRateLimitEngine, AsyncBaseRateLimitEngine
from dayu.cores.rlock import EnableRlock
from dayu.engines.mixin import TimeWindowsMixin

LOG = logging.getLogger(__name__)


class TimeWindowsRateLimitEngine(BaseRateLimitEngine, TimeWindowsMixin):  # 时间窗限流
    def __init__(self, limit, per, clock, wait, need_lock, queue):
        lock = EnableRlock(need_lock)
        super(TimeWindowsRateLimitEngine, self).__init__(limit=limit, per=per, clock=clock, lock_=lock)
        self.wait = wait
        self.func_counts = 0
        self.func_calls = queue


class AsyncTimeWindowsRateLimitEngine(AsyncBaseRateLimitEngine, TimeWindowsMixin):  # 时间窗限流
    def __init__(self, limit, per, clock, wait, queue):
        super(AsyncTimeWindowsRateLimitEngine, self).__init__(limit=limit, per=per, clock=clock, lock_=asyncio.Lock())
        self.wait = wait
        self.func_counts = 0
        self.func_calls = queue
