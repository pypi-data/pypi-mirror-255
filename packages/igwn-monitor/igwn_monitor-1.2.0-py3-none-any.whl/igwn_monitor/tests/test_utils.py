# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2023)

"""Tests for :mod:`igwn_monitor.utils`.
"""

import pytest

from .. import utils as imp_utils


@pytest.mark.parametrize(("args", "result"), [
    # simple key value
    (
        ({"label": "value"},),
        "'label'=value",
    ),
    # value and thresholds with separate unit spec
    (
        ({"time": (1.23, 5, 10)}, "s"),
        "'time'=1.23s;5;10",
    ),
    # multiple key/value pairs
    (
        ({"label": "value", "label2": ('10s', '15', '20')},),
        "'label'=value 'label2'=10s;15;20",
    )
])
def test_format_performance_metrics(args, result):
    assert imp_utils.format_performance_metrics(*args) == result
