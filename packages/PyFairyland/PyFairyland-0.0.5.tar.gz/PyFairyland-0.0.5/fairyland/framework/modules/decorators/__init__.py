# coding: utf8
"""
@ File: __init__.py
@ Editor: PyCharm
@ Author: Austin (From Chengdu.China) https://fairy.host
@ HomePage: https://github.com/AustinFairyland
@ OS: Linux Ubunut 22.04.4 Kernel 6.2.0-36-generic 
@ CreatedTime: 2023/11/25
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

from .DecoratorsModules import MethodRunTimeDecorators
from .DecoratorsModules import MethodTipsDecorators

__all__: list = [
    "MethodRunTimeDecorators",
    "MethodTipsDecorators",
]
