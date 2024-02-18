<!--
SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
SPDX-License-Identifier: BSD-2-Clause
-->

# Create a virtual environment to run Tox

\[[Home][ringlet-vetox] | [Download][ringlet-download] | [GitLab][gitlab] | [PyPI][pypi] | [ReadTheDocs][readthedocs]\]

## Overview

The `vetox` tool creates a virtual environment, installs a suitable
version of Tox within it, and then runs Tox with the specified arguments.
It does not use any modules outside of the Python standard library, so
it is suitable for use when testing with different Python versions.

Note that the `vetox` tool's main file, the `src/vetox/__main__.py` file in
the source distribution, may be copied into another project's source tree and
invoked using a Python 3.x interpreter.

## Invocation

The `vetox` tool accepts two subcommands: `run` and `run-parallel`,
as well as a `-c` / `--conf` option with the path to a `tox.ini` file.
Any positional arguments after the `run` or `run-parallel` subcommand are
passed on to Tox unmodified.

## Examples

Run Tox in an ephemeral virtual environment, use the `tox.ini` file found in
the current working directory, run all the default Tox environments in parallel:

``` sh
vetox run-parallel
```

Same, but use Tox 3.x and pass it some environment selection options:

``` sh
vetox run-parallel -t '>= 3, < 4' -- -e first,second
```

Use the `tox.ini` file in the parent directory, run the test environments
sequentially, one by one:

``` sh
vetox -c ../tox.ini run
```

If the `src/vetox/__main__.py` file was copied to another project, it may be
used to run that project's test suite:

``` sh
python3 tests/vetox.py run-parallel
```

Display the list of features supported by the `vetox` tool in a format
compatible with the [feature-check](https://devel.ringlet.net/misc/feature-check)
tool:

``` sh
vetox features
```

If the `src/vetox/__main__.py` file was copied to another project, it may be
used to run that project's test suite:

``` sh
python3 tests/vetox.py run-parallel
```

## Contact

The `vetox` tool was written by [Peter Pentchev][roam].
It is developed in [a GitLab repository][gitlab]. This documentation is
hosted at [Ringlet][ringlet-vetox] with a copy at [ReadTheDocs][readthedocs].

[roam]: mailto:roam@ringlet.net "Peter Pentchev"
[gitlab]: https://gitlab.com/ppentchev/vetox "The vetox GitLab repository"
[pypi]: https://pypi.org/project/vetox/ "The vetox Python Package Index page"
[readthedocs]: https://vetox.readthedocs.io/ "The vetox ReadTheDocs page"
[ringlet-vetox]: https://devel.ringlet.net/devel/vetox/ "The Ringlet vetox homepage"
[ringlet-download]: https://devel.ringlet.net/devel/vetox/ "The Ringlet vetox download page"
