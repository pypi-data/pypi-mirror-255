# coding: utf8
""" 
@File: TypeAnnotation.py
@Editor: PyCharm
@Author: Austin (From Chengdu.China) https://fairy.host
@HomePage: https://github.com/AustinFairyland
@OperatingSystem: Windows 11 Professional Workstation 23H2 Canary Channel
@CreatedTime: 2024-02-05
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

import typing
import types

from pymysql.connections import Connection as MySQLConnectionObject
from pymysql.cursors import Cursor as MySQLCursorObject
from psycopg2.extensions import connection as PostgreSQLConnectionObject
from psycopg2.extensions import cursor as PostgreSQLCursorObject

SQLConnectionType = typing.Union[MySQLConnectionObject, PostgreSQLConnectionObject]
SQLCursorType = typing.Union[MySQLCursorObject, PostgreSQLCursorObject]
