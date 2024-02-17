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

from .AbnormalModules import ProjectError
from .AbnormalModules import ParameterError
from .AbnormalModules import ReadFileError
from .AbnormalModules import DataSourceError
from .AbnormalModules import SQLExecutionError

__all__ = [
    "ProjectError",
    "ParameterError",
    "ReadFileError",
    "DataSourceError",
    "SQLExecutionError",
]
