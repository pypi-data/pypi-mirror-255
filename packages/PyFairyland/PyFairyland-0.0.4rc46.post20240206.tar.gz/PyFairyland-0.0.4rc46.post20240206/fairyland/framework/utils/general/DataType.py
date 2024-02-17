# coding: utf8
""" 
@ File: DataType.py
@ Editor: PyCharm
@ Author: Austin (From Chengdu.China) https://fairy.host
@ HomePage: https://github.com/AustinFairyland
@ OS: Windows 11 Professional Workstation 22H2
@ CreatedTime: 2023-09-11
"""
from __future__ import annotations

from typing import Union, Any, Callable
from types import FunctionType, MethodType

import os
import sys
import warnings
import platform
import asyncio

sys.dont_write_bytecode = True
warnings.filterwarnings("ignore")
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class DataTypeUtils:
    """DataTypeUtils"""

    @staticmethod
    def api_results():
        results = {"status": "failure", "code": 500, "data": None}
        return results

    @staticmethod
    def data_string():
        results = str()
        return results

    @staticmethod
    def data_integer():
        results = int()
        return results

    @staticmethod
    def data_float():
        results = float()
        return results

    @staticmethod
    def data_boolean():
        results = bool()
        return results

    @staticmethod
    def data_list() -> list[Any]:
        results: list[Any] = []
        return results

    @staticmethod
    def data_tuple():
        results: tuple[Any] = ()
        return results

    @staticmethod
    def data_set():
        results: set[Any] = set()
        return results

    @staticmethod
    def data_dict():
        results: dict[Any, Any] = {}
        return results

    @staticmethod
    def data_none():
        return None

    @staticmethod
    def data_byte():
        results = bytes()
        return results

    @staticmethod
    def data_bytearray():
        results = bytearray()
        return results

    @staticmethod
    def data_complex():
        results = complex()
        return results
