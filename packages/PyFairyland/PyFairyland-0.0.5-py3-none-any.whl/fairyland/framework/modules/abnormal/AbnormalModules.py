# coding: utf8
"""
@ File: AbnormalModules.py
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


class ProjectError(Exception):
    def __init__(self, message: str = "Internal error."):
        self.__prompt = f"{self.__class__.__name__}: {message}"

    def __str__(self):
        return self.__prompt


class ParameterError(ProjectError):
    def __init__(self, message: str = "Invalid parameter."):
        super().__init__(message=message)


class ReadFileError(ProjectError):
    def __init__(self, message: str = "Reading file error."):
        super().__init__(message=message)


class DataSourceError(ProjectError):
    def __init__(self, message: str = "Data source error."):
        super().__init__(message=message)


class SQLExecutionError(ProjectError):

    def __init__(self, message: str = "SQL exection error."):
        super().__init__(message=message)
