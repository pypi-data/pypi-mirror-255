# coding: utf8
""" 
@File: DjangoModdleware.py
@Editor: PyCharm
@Author: Austin (From Chengdu.China) https://fairy.host
@HomePage: https://github.com/AustinFairyland
@OperatingSystem: Windows 11 Professional Workstation 23H2 Canary Channel
@CreatedTime: 2024-01-28
"""
from __future__ import annotations

import os
import sys
import typing
import warnings
import platform
import asyncio

sys.dont_write_bytecode = True
warnings.filterwarnings("ignore")
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import types
import typing

from typing import Union, Any, Callable
from types import FunctionType, MethodType
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.utils.deprecation import MiddlewareMixin
import json

from fairyland.framework.modules.journal import Journal


class DjangoLoguruMiddleware(MiddlewareMixin):
    """Django Logging Middleware"""

    def __init__(self, get_response: Union[HttpResponse, None]):
        super().__init__(get_response=get_response)

    # def __call__(self, request: HttpRequest, *args: Any, **kwargs: Any):
    #     self.__request_logs(request)
    #     response: HttpResponse = self.__function(request, *args, **kwargs)
    #     return response

    def __request_logs(self, request: HttpRequest):
        __start = f"===== API: {request.path_info} ====="
        __end = "=" * __start.__len__()

        __method = request.method.upper()

        __HEADERS = request.headers
        __MATE = request.META

        __content_type: str = __HEADERS.get("Content-Type")

        Journal.info(__start)
        Journal.info(f"Request Address: {__MATE.get('PATH_INFO')}")
        Journal.info(f"Request Method: {__MATE.get('REQUEST_METHOD')}")
        Journal.debug(f"Request Headers: {__HEADERS}")
        Journal.debug(f"Request User-Agent: {__MATE.get('HTTP_USER_AGENT')}")
        Journal.debug(f"Request Content-Type: {__MATE.get('CONTENT_TYPE')}")
        Journal.info(f"Request Remote-IP: {__MATE.get('REMOTE_ADDR')}")
        Journal.info(f"Request Remote-Host: {__MATE.get('REMOTE_HOST')}")
        Journal.debug(f"Request Accept: {__MATE.get('HTTP_ACCEPT')}")
        Journal.debug(f"Request Accept-Language: {__MATE.get('HTTP_ACCEPT_LANGUAGE')}")
        Journal.debug(f"Request Accept-Encoding: {__MATE.get('HTTP_ACCEPT_ENCODING')}")
        Journal.debug(f"Request Connection: {__MATE.get('HTTP_CONNECTION')}")
        Journal.debug(f"Request Gateway-Interface: {__MATE.get('GATEWAY_INTERFACE')}")
        Journal.debug(f"Request Http-Host: {__MATE.get('HTTP_HOST')}")
        Journal.debug(f"Request Server-Port: {__MATE.get('SERVER_PORT')}")
        Journal.trace(f"Cookies: {request.COOKIES}")
        if __method in ("GET", "PATCH", "DELETE", "HEAD", "OPTIONS"):
            __request_parameters = request.GET
            Journal.trace(f"Payload: {__request_parameters.dict()}")
        elif __method in ("POST", "PUT"):
            __request_parameters = request.POST
            __request_bodydata = request.body.decode()
            __line_sep = "..." if not __request_bodydata else "\n"
            if __content_type.split(";")[0] == "multipart/form-data":
                Journal.trace(f"Payload multipart/form-data: {__request_parameters.dict()}")
            elif __content_type == "application/x-www-form-urlencoded":
                __payload_data = {k: v for k, v in (pair.split("=") for pair in __request_bodydata.split("&"))}
                Journal.trace(f"Payload application/x-www-form-urlencoded: {__payload_data}")
            elif __content_type == "text/plain":
                Journal.trace("".join(("Payload text/plain: ", __line_sep, __request_bodydata)))
            elif __content_type == "application/javascript":
                Journal.trace("".join(("Payload application/javascript: ", __line_sep, __request_bodydata)))
            elif __content_type == "text/html":
                Journal.trace("".join(("Payload text/html: ", __line_sep, __request_bodydata)))
            elif __content_type == "application/xml":
                Journal.trace("".join(("Payload application/xml: ", __line_sep, __request_bodydata)))
            elif __content_type == "application/json":
                Journal.trace(f"Payload application/json: {json.loads(__request_bodydata)}")
            Journal.trace(f"Payload file-stream: {request.FILES}")

        Journal.info(__end)

    def process_request(self, request: HttpRequest):
        self.__request_logs(request)

    def process_response(self, request: HttpRequest, response: HttpResponse):
        return response
