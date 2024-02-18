# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2023)
# SPDX-License-Identifier: MIT

"""Python utilities for IGWN monitoring with Nagios-like systems.
"""

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"
__license__ = "MIT"

try:
    from ._version import version as __version__
except ModuleNotFoundError:  # development mode
    __version__ = "dev"
