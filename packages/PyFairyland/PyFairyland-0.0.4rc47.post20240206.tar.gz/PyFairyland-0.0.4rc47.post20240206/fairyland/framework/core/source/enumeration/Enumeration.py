# coding: utf8
""" 
@File: Enumeration.py
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

from fairyland.framework.core.inheritance.enumsource import StringEnum
from fairyland.framework.core.source.packaging import InstallPackageSource


class ProjectEnum(StringEnum):
    """ProjectEnum"""

    version = InstallPackageSource.release_version


class PackageEnum(StringEnum):
    """PackageEnum"""

    name = InstallPackageSource.name
    release_version = InstallPackageSource.release_version
    test_version = InstallPackageSource.test_version
    alpha_version = InstallPackageSource.alpha_version
    beta_version = InstallPackageSource.beta_version
