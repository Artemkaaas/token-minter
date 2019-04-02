import os
import platform

import asyncio
from ctypes import cdll

PROTOCOL_VERSION = 2

EXTENSION = {"darwin": ".dylib", "linux": ".so", "win32": ".dll", 'windows': '.dll'}
INITIAL_DIR = os.path.abspath('..')
PAYMENT_LIBRARY = 'libsovtoken'
PAYMENT_PREFIX = 'pay:sov:'

loop = asyncio.get_event_loop()


def file_ext():
    your_platform = platform.system().lower()
    return EXTENSION[your_platform] if (your_platform in EXTENSION) else '.so'


def load_plugin():
    try:
        payment_plugin = cdll.LoadLibrary(PAYMENT_LIBRARY + file_ext())
        payment_plugin.sovtoken_init()
    except Exception:
        raise Exception('Cannot find libsovtoken library')


def run_coroutine(coroutine):
    return loop.run_until_complete(coroutine)
