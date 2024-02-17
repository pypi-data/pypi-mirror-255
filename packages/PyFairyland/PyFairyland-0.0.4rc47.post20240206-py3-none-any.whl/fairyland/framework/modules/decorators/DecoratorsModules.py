# coding: utf8
"""
@ File: DecoratorsModules.py
@ Editor: PyCharm
@ Author: Austin (From Chengdu.China) https://fairy.host
@ HomePage: https://github.com/AustinFairyland
@ OS: Linux Ubunut 22.04.4 Kernel 6.2.0-36-generic 
@ CreatedTime: 2023/11/25
"""
from __future__ import annotations

import sys
import types
import warnings
import platform
import asyncio

sys.dont_write_bytecode = True
warnings.filterwarnings("ignore")
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from types import FunctionType, MethodType
from typing import Union, Any, Callable

import time

from ..journal import Journal


class MethodRunTimeDecorators:
    """
    This class decorators is used for measuring and logging the execution time of functions.
        类装饰器，用于测量和记录函数的运行时间。
    """

    def __new__(
        cls,
        function: Union[FunctionType, MethodType],
        *args: Any,
        **kwargs: Any,
    ) -> Callable[..., Any]:
        """
        Called when the decorators is applied to a function. Creates and returns a wrapper function.
            当装饰器应用于函数时调用。创建并返回包装函数。
        @param function: The function to be decorated. | 被装饰的函数。
        @type function: Union[FunctionType, MethodType]
        @param args: Positional arguments for the decorated function. | 被装饰函数的位置参数。
        @type args: Any
        @param kwargs: Keyword arguments for the decorated function. | 被装饰函数的关键字参数。
        @type kwargs: Any
        @return: The wrapper function. | 包装后的函数。
        @rtype: Callable[..., Any]
        """

        def warpper(*args: Any, **kwargs: Any) -> Any:
            """
            Wrapper function that logs the execution time of the decorated function.
                包装函数，记录被装饰函数的执行时间。
            @param args: Positional arguments for the decorated function. | 被装饰函数的位置参数。
            @type args: Any
            @param kwargs: Keyword arguments for the decorated function. | 被装饰函数的关键字参数。
            @type kwargs: Any
            @return: The return value of the decorated function. | 被装饰函数的返回值。
            @rtype: Any
            """
            start_time = time.time()
            result = function(*args, **kwargs)
            end_time = time.time()
            elapsed_time = end_time - start_time
            Journal.success(f"This method ran for {elapsed_time} seconds")
            return result

        return warpper


class MethodTipsDecorators:
    def __init__(self, annotation: str = "A method"):
        self.__annotation = annotation

    # @MethodRunTimeDecorators
    def __call__(
        self,
        function: Union[FunctionType, MethodType],
        *args: Any,
        **kwargs: Any,
    ) -> Callable[..., Any]:
        """
        The method decorators logic.
            方法装饰器的逻辑。
        @param function: The function to be decorated. | 被装饰的函数。
        @type function: Union[FunctionType, MethodType]
        @param args: Positional arguments for the decorated function. | 被装饰函数的位置参数。
        @type args: Any
        @param kwargs: Keyword arguments for the decorated function. | 被装饰函数的关键字参数。
        @type kwargs: Any
        @return: The wrapper function. | 包装后的函数。
        @rtype: Callable[..., Any]
        """

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """
            Wrapper function that logs the execution status of the decorated function.
                包装函数，记录被装饰函数的执行状态。
            @param args: Positional arguments for the decorated function. | 被装饰函数的位置参数。
            @type args: Any
            @param kwargs: Keyword arguments for the decorated function. | 被装饰函数的关键字参数。
            @type kwargs: Any
            @return: The return value of the decorated function. | 被装饰函数的返回值。
            @rtype: Any
            """
            try:
                Journal.debug(f"Action Running {self.__annotation}")
                results = function(*args, **kwargs)
                Journal.success(f"Success Running {self.__annotation}")
            except Exception as error:
                Journal.error(f"Failure Running {self.__annotation}")
                raise
            return results

        return wrapper
