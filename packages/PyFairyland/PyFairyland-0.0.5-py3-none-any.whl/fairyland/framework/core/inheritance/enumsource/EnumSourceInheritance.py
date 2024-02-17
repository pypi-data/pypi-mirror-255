# coding: utf8
""" 
@File: EnumSourceInheritance.py
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
from typing import Union, List, Tuple, Any
from enum import Enum


class BaseEnum(Enum):
    """Base class for custom Enum types."""

    def describe(self) -> Tuple[str]:
        """
        Returns a tuple with the name and value of the Enum member.
        @return: Tuple with the name and value of the Enum member.
        @rtype: Tuple[str]
        """
        return self.name, self.value

    @classmethod
    def default(cls):
        """
        Abstract method to be implemented in subclasses.
        Returns the default value for the Enum.
        @return: Default value for the Enum.
        @rtype: Any
        """
        raise NotImplementedError("Implement it in a subclass.")

    @classmethod
    def members(cls, exclude_enums: Union[List[str], None] = None, only_value: bool = False) -> Tuple[Union[BaseEnum, str, int, float, bool]]:
        """
        Returns a tuple with all members of the Enum.
        @param exclude_enums: List of members to exclude from the result.
        @type exclude_enums: Union[List[str], None]
        @param only_value: If True, returns only the values of the members.
        @type only_value: bool
        @return: Tuple with all members of the Enum.
        @rtype: Tuple[Union[BaseEnum, str, int, float, bool]]
        """
        member_list: List[cls] = list(cls)
        if exclude_enums:
            member_list = tuple([member for member in member_list if member not in exclude_enums])
        if only_value:
            member_list = tuple([member.value for member in member_list])
        return member_list

    @classmethod
    def names(cls) -> Tuple[str]:
        """
        Returns a tuple with the names of all members of the Enum.
        @return: Tuple with the names of all members of the Enum.
        @rtype: Tuple[str]
        """
        return tuple(cls._member_names_)

    @classmethod
    def values(cls, exclude_enums: Union[List[str], None] = None) -> Tuple[str, int, float, bool]:
        """
        Returns a tuple with the values of all members of the Enum.
        @param exclude_enums: List of members to exclude from the result.
        @type exclude_enums: Union[List[str], None]
        @return: Tuple with the values of all members of the Enum.
        @rtype: Tuple[str, int, float, bool]
        """
        return cls.members(exclude_enums=exclude_enums, only_value=True)


class StringEnum(str, BaseEnum):
    """String Enum"""

    pass


class IntegerEnum(int, BaseEnum):
    """Integer Enum"""

    pass
