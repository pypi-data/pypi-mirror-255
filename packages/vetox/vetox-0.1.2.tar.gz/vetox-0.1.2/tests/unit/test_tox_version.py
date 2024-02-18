# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Test the routines that examine the required Tox version."""

from __future__ import annotations

import pytest

from vetox import __main__ as vmain

from . import util


@pytest.mark.parametrize(
    ("line", "expected"),
    [("minversion = 4.2", "4.2"), ("# nothing", "4.1"), ("min_version = 5.3", "5.3")],
)
def test_tox_version(*, line: str, expected: str) -> None:
    """Examine a `tox.ini` file, obtain the minimum version required to run Tox."""
    with util.tempd_and_config(use_tox3=False) as (_, cfg):
        cfg.conf.write_text(
            f"""
[tox]
{line}
""",
            encoding="UTF-8",
        )
        assert vmain.get_tox_min_version(cfg) == expected
