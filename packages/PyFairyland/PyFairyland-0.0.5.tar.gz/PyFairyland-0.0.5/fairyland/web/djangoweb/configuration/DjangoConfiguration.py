# coding: utf8
""" 
@File: DjangoConfiguration.py
@Editor: PyCharm
@Author: Austin (From Chengdu.China) https://fairy.host
@HomePage: https://github.com/AustinFairyland
@OperatingSystem: Windows 11 Professional Workstation 23H2 Canary Channel
@CreatedTime: 2024-01-28
"""
from __future__ import annotations

import os
import sys
import warnings
import platform
import asyncio

sys.dont_write_bytecode = True
warnings.filterwarnings("ignore")
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from typing import Union, Any, Callable
from types import FunctionType, MethodType


class DjangoPublicConfiguration:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "logs": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "stream": open("logs/django-service.log", "a+"),
            },
        },
        "loggers": {
            "django": {
                "handlers": ["logs"],
                "level": "DEBUG",
                "propagate": True,
            },
        },
    }
