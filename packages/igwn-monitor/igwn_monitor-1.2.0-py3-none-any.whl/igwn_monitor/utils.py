# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2023)
# SPDX-License-Identifier: MIT

"""Utilities for IGWN monitoring.
"""

from enum import IntEnum


class NagiosStatus(IntEnum):
    """Nagios exit codes and status strings.
    """
    OK = 0
    WARNING = 1
    CRITICAL = 2
    UNKNOWN = 3


def _format_metric_value(value, unit=None):
    if isinstance(value, (list, tuple)):
        out = ""
        for val in value:
            out += ";" + _format_metric_value(val, unit=unit)
            unit = None
        return out.lstrip(";")
    if value is None:
        return ""
    return str(value) + str(unit or "")


def format_performance_metrics(metrics, unit=None):
    """Format a dict of performance metrics

    See https://icinga.com/docs/icinga-2/latest/doc/05-service-monitoring/#performance-data-metrics.

    The metrics should be a `dict` of label, value pairs, where the value
    can be either a `str`, which is formatted verbatim, or a sequence
    (e.g. `tuple`) where the values are formatted ';'-delimited.

    Examples
    --------
    >>> format_performance_metrics({"label": "value"})
    "'label'=value"
    >>> format_performance_metrics({"time": 1.23}, unit="s")
    "'time'=1.23s"
    >>> format_performance_metrics({"label": "value", "label2": ('10s', '15', '20')})
    "'label'=value 'label2'=10s;15;20"
    """  # noqa: E501
    formatted = []
    for label, value in metrics.items():
        formatted.append(f"'{label}'={_format_metric_value(value, unit=unit)}")
    return " ".join(formatted)
