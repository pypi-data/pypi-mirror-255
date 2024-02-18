# -*- coding: utf-8 -*-

"""Tests for the `check_command` plugin.
"""

import re
import sys

import pytest

from ...plugins import check_command


@pytest.mark.parametrize(("args", "status", "message"), [
    # OK
    pytest.param(
        (
            "--verbose", "--empty-env",
            sys.executable, "--version",
        ),
        0,
        "Command succeeded .*Python 3",
        id="ok",
    ),
    # fail
    pytest.param(
        (
            sys.executable, "-c", "import sys; sys.exit(10)",
        ),
        2,
        r"Command failed \(exited with code 10\)",
        id="fail",
    ),
    # fail as warning
    pytest.param(
        (
            "--warning-code", "10",
            sys.executable, "-c", "import sys; sys.exit(10)",
        ),
        1,
        r"Command failed \(exited with code 10\)",
        id="warning",
    ),
    # timeout
    pytest.param(
        (
            "--timeout", "1",
            sys.executable, "-c", "import time; time.sleep(10)",
        ),
        2,
        r"Command timed out",
        id="timeout",
    ),
    # timeout unknown
    pytest.param(
        (
            "--timeout", "1", "--timeout-unknown",
            sys.executable, "-c", "import time; time.sleep(10)",
        ),
        3,
        r"Command timed out",
        id="timeout unknown",
    ),
    # executable not found
    pytest.param(
        (
            "--verbose",
            "badbadbad",
        ),
        3,
        "Failed to run command .* No such file or directory: 'badbadbad'",
        id="filenotfound",
    )
])
def test_check_command(capsys, args, status, message):
    """Check that `check_command` works.
    """
    # run the check
    ret = check_command.main(args)
    assert ret == status

    # ensure that the most recent file is found
    stdout = capsys.readouterr().out
    assert re.match(message, stdout, re.DOTALL)
