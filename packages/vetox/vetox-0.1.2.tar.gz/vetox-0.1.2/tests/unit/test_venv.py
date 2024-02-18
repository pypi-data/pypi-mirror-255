# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Test the routines that create and populate the virtual environment."""

from __future__ import annotations

import dataclasses
import functools
import itertools
import json
import pathlib
import subprocess
import sys
import tempfile
import typing

import pytest

from vetox import __main__ as vmain

from . import util


if typing.TYPE_CHECKING:
    from typing import Final


ENV_FIRST: Final = "light-shined"
ENV_SECOND: Final = "rarely"

OUTPUT_FIRST: Final = "I had a light that shined across my mind"
OUTPUT_SECOND: Final = "Rarely see it any more"


@dataclasses.dataclass(frozen=True)
class ToxCase:
    """A single test case for running Tox via the vetox tool or functions."""

    parallel: bool
    """Should the Tox environments be run in parallel."""

    args: list[str]
    """Additional command-line arguments to pass to Tox."""

    expected: list[str]
    """Words and phrases that are expected to be in the output."""

    not_expected: list[str]
    """Words and phrases that are not expected to be in the output."""


TEST_CASES: Final = [
    ToxCase(
        parallel=False,
        args=[],
        expected=[ENV_FIRST, ENV_SECOND, OUTPUT_FIRST, OUTPUT_SECOND],
        not_expected=[],
    ),
    ToxCase(
        parallel=True,
        args=[],
        expected=[ENV_FIRST, ENV_SECOND],
        not_expected=[OUTPUT_FIRST, OUTPUT_SECOND],
    ),
    ToxCase(
        parallel=False,
        args=["-e", ENV_FIRST],
        expected=[ENV_FIRST, OUTPUT_FIRST],
        not_expected=[ENV_SECOND, OUTPUT_SECOND],
    ),
    ToxCase(
        parallel=False,
        args=["-e", ENV_SECOND],
        expected=[ENV_SECOND, OUTPUT_SECOND],
        not_expected=[ENV_FIRST, OUTPUT_FIRST],
    ),
    ToxCase(
        parallel=True,
        args=["-e", ENV_FIRST],
        expected=[ENV_FIRST],
        not_expected=[ENV_SECOND, OUTPUT_FIRST, OUTPUT_SECOND],
    ),
    ToxCase(
        parallel=True,
        args=["-e", ENV_SECOND],
        expected=[ENV_SECOND],
        not_expected=[ENV_FIRST, OUTPUT_FIRST, OUTPUT_SECOND],
    ),
]
"""The tests to run."""


def prepare_config(conf: pathlib.Path, *, use_tox3: bool) -> None:
    """Prepare the Tox configuration file, requiring Tox 3.x if specified."""
    orig_path: Final = pathlib.Path(__file__).parent.parent / "data/tox.ini"
    orig: Final = orig_path.read_text(encoding="UTF-8")
    actual: Final = orig.replace(" \\\n", "\n") if use_tox3 else orig
    conf.write_text(actual, encoding="UTF-8")


@functools.lru_cache
def pip_cmd(venv: pathlib.Path) -> list[pathlib.Path | str]:
    """Get the command to run `pip` within the virtual environment."""
    return [venv / "bin/python3", "-m", "pip"]


def run_pip_list(venv: pathlib.Path) -> dict[str, str]:
    """List the packages installed in the virtual environment and their versions."""
    contents: Final = subprocess.check_output(
        [*pip_cmd(venv), "list", "--format=json"],
        encoding="UTF-8",
    )
    return {pkg["name"]: pkg["version"] for pkg in json.loads(contents)}


@pytest.mark.parametrize(("tcase", "use_tox3"), itertools.product(TEST_CASES, [False, True]))
def test_venv_create_install_run_tox(*, tcase: ToxCase, use_tox3: bool) -> None:
    """Create a virtual environment, examine the packages installed within."""
    with util.tempd_and_config(use_tox3=use_tox3) as (_, cfg):
        prepare_config(cfg.conf, use_tox3=use_tox3)

        venv: Final = vmain.create_and_update_venv(cfg)
        assert cfg.tempd in venv.parents

        # Make sure that "pip" is listed as installed in the virtual environment
        # (by invoking "pip"... yeah, well, it is not supposed to fail, is it now?)
        pkgs: Final[dict[str, str]] = run_pip_list(venv)
        assert "pip" in pkgs

        # Now make sure that the package versions remain the same after upgrading them all
        subprocess.check_call([*pip_cmd(venv), "install", "-U", "--", *pkgs.keys()])
        upd_pkgs: Final[dict[str, str]] = run_pip_list(venv)
        assert upd_pkgs == pkgs

        vmain.install_tox(cfg, venv)

        # Make sure that "tox" is now listed as installed in the virtual environment
        tox_pkgs: Final[dict[str, str]] = run_pip_list(venv)
        assert "tox" in tox_pkgs

        tox_cmdline: Final = vmain.get_tox_cmdline(
            cfg,
            venv,
            parallel=tcase.parallel,
            args=tcase.args,
        )
        output: Final = subprocess.check_output(tox_cmdline, encoding="UTF-8")
        for item in tcase.expected:
            assert item in output
        for item in tcase.not_expected:
            assert item not in output


@pytest.mark.parametrize(("tcase", "use_tox3"), itertools.product(TEST_CASES, [False, True]))
def test_run(*, tcase: ToxCase, use_tox3: bool) -> None:
    """Create a temporary directory, copy the tox.ini file, run the command-line tool."""
    with tempfile.TemporaryDirectory() as tempd_obj:
        conf: Final = pathlib.Path(tempd_obj) / "tox.ini"
        prepare_config(conf, use_tox3=use_tox3)

        tox3_opts: Final = ["--tox-req", ">= 3, < 4"] if use_tox3 else []
        output: Final = subprocess.check_output(
            [
                sys.executable,
                "-m",
                "vetox",
                "-c",
                conf,
                "run-parallel" if tcase.parallel else "run",
                *tox3_opts,
                "--",
                *tcase.args,
            ],
            encoding="UTF-8",
        )
        for item in tcase.expected:
            assert item in output
        for item in tcase.not_expected:
            assert item not in output
