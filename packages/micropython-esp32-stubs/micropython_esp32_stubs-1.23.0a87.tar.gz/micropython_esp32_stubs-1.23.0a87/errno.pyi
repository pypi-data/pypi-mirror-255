"""
System error codes.

MicroPython module: https://docs.micropython.org/en/v1.23.0.preview/library/errno.html

CPython module: :mod:`python:errno` https://docs.python.org/3/library/errno.html .

This module provides access to symbolic error codes for `OSError` exception.
A particular inventory of codes depends on :term:`MicroPython port`.

---
Module: 'errno' on micropython-v1.23.0-preview-esp32-ESP32_GENERIC
"""
# MCU: {'family': 'micropython', 'version': '1.23.0-preview', 'build': 'preview.6.g3d0b6276f', 'ver': '1.23.0-preview-preview.6.g3d0b6276f', 'port': 'esp32', 'board': 'ESP32_GENERIC', 'cpu': 'ESP32', 'mpy': 'v6.2', 'arch': 'xtensawin'}
# Stubber: v1.16.3
from __future__ import annotations
from _typeshed import Incomplete
from typing import Dict

ENOBUFS: int = 105
ENODEV: int = 19
ENOENT: int = 2
EISDIR: int = 21
EIO: int = 5
EINVAL: int = 22
EPERM: int = 1
ETIMEDOUT: int = 116
ENOMEM: int = 12
EOPNOTSUPP: int = 95
ENOTCONN: int = 128
errorcode: dict = {}
EAGAIN: int = 11
EALREADY: int = 120
EBADF: int = 9
EADDRINUSE: int = 112
EACCES: int = 13
EINPROGRESS: int = 119
EEXIST: int = 17
EHOSTUNREACH: int = 118
ECONNABORTED: int = 113
ECONNRESET: int = 104
ECONNREFUSED: int = 111
