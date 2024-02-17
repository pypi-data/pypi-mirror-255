import asyncio
import logging

from dayu.exceptions import RateLimitException

LOG = logging.getLogger(__name__)


class TimeWindowsMixin(object):
    def sliding_window(self):
        last = None
        while self.func_counts > 0:  # 滑窗
            cur = self.clock()
            last = self.func_calls[0]
            period = cur - last
            if self.in_period(period, self.period):
                break
            self.finish_func()
        return last

    def finish_func(self):
        call_time = self.func_calls.popleft()
        self.func_counts -= 1
        return call_time

    def commit_func(self, call_time):
        self.func_counts += 1
        self.func_calls.append(call_time)

    def process_limit(self):
        last = self.sliding_window()
        if last and self.func_counts >= self.limit:
            cur = self.clock()
            period = cur - last
            if self.in_period(period, self.period):
                error_message = f"[{self._func_name}] rate limit warning: limit {self.limit}/{self.period}s, real {self.func_counts}/{period}s"
                if self.wait:
                    sleep_seconds = self.period - period * 0.8  # 延长 0.2倍的时间
                    LOG.info(f"[{error_message}, sleep {sleep_seconds}")
                    yield sleep_seconds
                else:
                    raise RateLimitException(error_message)


class UniformMixin(object):
    def commit_func(self, call_time):
        self.last = call_time

    def process_limit(self):
        if self.last:
            period = self.clock() - self.last
            if self.in_period(period, self.rate_limit):  # 限速
                sleep_seconds = self.rate_limit - period
                LOG.info(f"[{self._func_name}] uniform rate limit warning: limit {self.rate_limit}s，real {period}s, sleep {sleep_seconds}s")
                yield sleep_seconds
