# coding: utf8
""" 
@File: InstallPackage.py
@Editor: PyCharm
@Author: Austin (From Chengdu.China) https://fairy.host
@HomePage: https://github.com/AustinFairyland
@OperatingSystem: Windows 11 Professional Workstation 23H2 Canary Channel
@CreatedTime: 2024-02-06
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

from datetime import datetime


class InstallPackageSource:
    """InstallPackageSource"""

    # package name
    name = "PyFairyland"

    # version
    __major_number = 0
    __sub_number = 0
    __stage_number = 4
    __revise_number = 47

    if __revise_number.__str__().__len__() < 5:
        __nbit = 5 - __revise_number.__str__().__len__()
        __revise_number = "".join((("0" * __nbit), __revise_number.__str__()))
    else:
        __revise_number = __revise_number.__str__()
    __date_number = datetime.now().date().__str__().replace("-", "")
    __revise_after = "-".join((__revise_number.__str__(), __date_number))

    # version: (release_version, test_version, alpha_version, beta_version)
    release_version = ".".join((__major_number.__str__(), __sub_number.__str__(), __stage_number.__str__()))
    test_version = ".".join((release_version, "".join(("rc", __revise_after))))
    alpha_version = ".".join((release_version, "".join(("alpha", __revise_after))))
    beta_version = ".".join((release_version, "".join(("beta", __revise_after))))
