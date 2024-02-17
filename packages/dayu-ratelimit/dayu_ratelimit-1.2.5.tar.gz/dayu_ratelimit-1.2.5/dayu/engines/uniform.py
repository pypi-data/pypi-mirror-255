import asyncio
import logging
from dayu.cores.engine import BaseRateLimitEngine, AsyncBaseRateLimitEngine
from dayu.cores.rlock import EnableRlock
from dayu.engines.mixin import UniformMixin

LOG = logging.getLogger(__name__)


class UniformRateLimitEngine(BaseRateLimitEngine, UniformMixin):  # 匀速限流
    def __init__(self, limit, per, clock, wait, need_lock):
        super(UniformRateLimitEngine, self).__init__(limit=limit, per=per, clock=clock, lock_=EnableRlock(need_lock))
        self.rate_limit = self.period / self.limit
        self.last = None


class AsyncUniformRateLimitEngine(AsyncBaseRateLimitEngine, UniformMixin):  # 匀速限流
    def __init__(self, limit, per, clock, wait):
        super(AsyncUniformRateLimitEngine, self).__init__(limit=limit, per=per, clock=clock, lock_=asyncio.Lock())
        self.rate_limit = self.period / self.limit
        self.last = None
