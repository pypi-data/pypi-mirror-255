<!--
SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
SPDX-License-Identifier: BSD-2-Clause
-->

# Changelog

All notable changes to the vetox project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.2] - 2024-02-08

### Fixes

- Documentation:
    - drop some unneeded whitespace in code blocks

### Additions

- Add the `--tox-req` (`-t`) command-line option to specify PEP508-like
  version requirements for Tox itself, allowing e.g. Tox 3.x to be used.
- Test infrastructure:
    - also build the documentation in the second Tox stage
    - use Ruff 0.2.1 with no changes

## [0.1.1] - 2024-02-03

### Fixes

- Pass "vetox", not "logging-std", as the name of the main logger.

### Additions

- Documentation:
    - add a "Download" page

### Other changes

- Let Ruff insist on trailing commas.
- Documentation:
    - README.md: catch up with the main documentation page
- Test infrastructure:
    - use Ruff 0.2.0
        - disable another subprocess-related check
        - push some of the configuration settings into the new `ruff.lint.*`
          hierarchy
        - drop the override for the deprecated "no self use" check

## [0.1.0] - 2023-12-21

### Started

- First public release.

[Unreleased]: https://gitlab.com/ppentchev/vetox/-/compare/release%2F0.1.2...main
[0.1.2]: https://gitlab.com/ppentchev/vetox/-/compare/release%2F0.1.1...release%2F0.1.2
[0.1.1]: https://gitlab.com/ppentchev/vetox/-/compare/release%2F0.1.0...release%2F0.1.1
[0.1.0]: https://gitlab.com/ppentchev/vetox/-/tags/release%2F0.1.0
