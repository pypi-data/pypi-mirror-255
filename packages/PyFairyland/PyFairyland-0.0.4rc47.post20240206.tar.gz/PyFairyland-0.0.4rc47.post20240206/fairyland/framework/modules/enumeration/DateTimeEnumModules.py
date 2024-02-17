# coding: utf8
""" 
@File: DateTimeEnumModules.py
@Editor: PyCharm
@Author: Austin (From Chengdu.China) https://fairy.host
@HomePage: https://github.com/AustinFairyland
@OperatingSystem: Windows 11 Professional Workstation 23H2 Canary Channel
@CreatedTime: 2024-02-05
"""
from __future__ import annotations

import abc
import os
import sys
import warnings
import platform
import asyncio
from typing import Tuple

sys.dont_write_bytecode = True
warnings.filterwarnings("ignore")
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fairyland.framework.core.inheritance.enumsource import BaseEnum


class DateTimeFormatEnum(BaseEnum):
    """Datetime Format Enum"""

    date = "%Y-%m-%d"
    time = "%H:%M:%S"
    datetime = "%Y-%m-%d %H:%M:%S"

    date_CN = "%Y年%m月%d日"
    time_CN = "%H时%M分%S秒"
    datetime_CN = "%Y年%m月%d日 %H时%M分%S秒"

    @classmethod
    def default(cls):
        return cls.datetime.value
