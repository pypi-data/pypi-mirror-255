# coding: utf8
""" 
@ File: __init__.py
@ Editor: PyCharm
@ Author: Austin (From Chengdu.China) https://fairy.host
@ HomePage: https://github.com/AustinFairyland
@ OS: Windows 11 Professional Workstation 22H2
@ CreatedTime: 2023-09-11
"""
from __future__ import annotations

import sys
import warnings
import platform
import asyncio

sys.dont_write_bytecode = True
warnings.filterwarnings("ignore")
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from .DataType import DataTypeUtils
from .TypeAnnotation import SQLConnectionType
from .TypeAnnotation import SQLCursorType


__all__: list = [
    "DataTypeUtils",
    "SQLConnectionType",
    "SQLCursorType",
]
