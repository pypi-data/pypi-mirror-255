import asyncio
import sys
import time
from math import floor

from .rlock import EnableRlock


class BaseEngine(object):
    def __init__(self, limit, per, clock, lock_):
        self.lock = lock_
        self.limit = max(1, min(sys.maxsize, floor(limit)))
        self.period = max(1, per)
        self.clock = clock
        self._func_name = None

    @classmethod
    def in_period(cls, cur, max_limit):
        return 0 < cur < max_limit

    def set_func(self, func_name):
        self._func_name = func_name


class BaseRateLimitEngine(BaseEngine):
    def delay(self, seconds):
        last = self.clock()
        sleep_time = seconds / 100
        sleep_time = 0.001 if sleep_time > 0.001 else round(sleep_time, 3)
        if sleep_time == 0:
            sleep_time = 0.001

        while True:
            cur = self.clock()
            period = cur - last
            if period < 0:  # 重新计时
                last = self.clock()
                continue
            if period >= seconds:
                break
            left = seconds - period
            time.sleep(left if left < 0.001 else sleep_time)

    def run_limit(self):
        with self.lock:
            self._run_limit()

    def _run_limit(self):
        for sleep_seconds in self.process_limit():
            if sleep_seconds is not None:
                self.delay(sleep_seconds)
        self.commit_func(self.clock())


class AsyncBaseRateLimitEngine(BaseEngine):
    async def run_limit(self):
        async with self.lock:
            await self._run_limit()

    async def _run_limit(self):
        for sleep_seconds in self.process_limit():
            if sleep_seconds is not None:
                await asyncio.sleep(sleep_seconds)
        self.commit_func(self.clock())
