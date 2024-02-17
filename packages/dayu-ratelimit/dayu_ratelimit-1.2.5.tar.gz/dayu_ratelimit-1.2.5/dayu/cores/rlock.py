try:
    from _thread import RLock
except ImportError:
    from threading import RLock


class EnableRlock(object):
    def __init__(self, enable):
        self.lock = RLock() if enable else None

    def __enter__(self):
        if self.lock:
            self.lock.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.lock:
            self.lock.release()