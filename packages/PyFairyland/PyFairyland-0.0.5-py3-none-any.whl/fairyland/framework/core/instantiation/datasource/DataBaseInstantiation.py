# coding: utf8
""" 
@File: DataBaseInstantiation.py
@Editor: PyCharm
@Author: Austin (From Chengdu.China) https://fairy.host
@HomePage: https://github.com/AustinFairyland
@OperatingSystem: Windows 11 Professional Workstation 23H2 Canary Channel
@CreatedTime: 2023-10-12
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

import typing
import types
from typing import Union, Any, Callable, overload, List, Tuple, Dict
from abc import ABC, abstractmethod
import pymysql
import psycopg2

from fairyland.framework.core.inheritance.datasource import DataBaseSource
from fairyland.framework.modules.journal import Journal


class MySQLSource(DataBaseSource):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    def connect(self):
        try:
            connect = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset=self.charset,
                connect_timeout=self.connect_timeout,
            )
            Journal.success("MySQL Connect: OK")
        except Exception as error:
            Journal.error(error)
            raise
        return connect

    def execute(self, statement: str, parameters: Union[str, tuple, list, None] = None) -> None:
        self.cursor.execute(query=statement, args=parameters)


class PostgreSQLSource(DataBaseSource):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

    def connect(self):
        try:
            connect = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
            )
        except Exception as error:
            Journal.error(error)
            raise
        return connect

    def execute(self, statement: str, parameters: Union[str, tuple, list, None] = None) -> None:
        self.cursor.execute(query=statement, vars=parameters)
