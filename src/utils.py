import json
import os
import platform
import urllib.request

import asyncio
from ctypes import cdll

from src.constants import *

PROTOCOL_VERSION = 2

EXTENSION = {"darwin": ".dylib", "linux": ".so", "win32": ".dll", 'windows': '.dll'}
INITIAL_DIR = os.path.abspath('..')

loop = asyncio.get_event_loop()


def load_config():
    return json.loads(read_remote_file(CONFIG_URL))


def read_remote_file(url: str) -> str:
    return urllib.request.urlopen(url).read().decode()


def download_remote_file(url: str) -> str:
    path, _ = urllib.request.urlretrieve(url)
    return path


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
