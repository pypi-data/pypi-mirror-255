import sys
import time


def current():
    if sys.platform == "win32":
        # On Windows, the best timer is time.clock()
        return time.clock()
    else:
        # On most other platforms the best timer is time.time()
        return time.time()