# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2023)
# SPDX-License-Identifier: MIT

"""IGWN Monitoring Plugins.

The modules in this sub-package implement standalone monitoring plugins
that take in arbitrary arguments and should all return the same output:

- a `NagiosStatus` enum value, or `int`
- the message to display (can be many lines, `str`)

Each plugin module should be configured as a 'script' entry point in the
Python package metadata to provide a command-line interface that follows
the Monitoring Plugins Developement Guidelines as far as practical.
"""
