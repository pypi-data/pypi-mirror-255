<!--
SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
SPDX-License-Identifier: BSD-2-Clause
-->

# Changelog

All notable changes to the parse-stages project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.8] - 2024-02-08

### Additions

- Support parentheses in stage specifications, e.g. `(@check or @docs) and not @manual`
- Tentatively declare Python 3.13 as a supported version
- Documentation:
    - add a "Download" page
- Test suite:
    - vendor-import [the vetox testing tool](https://devel.ringlet.net/devel/vetox/)
    - add a Nix expression to run `vetox`

### Other changes

- Completely switch to Ruff for source code formatting
- Test suite:
    - use Ruff 0.2.1:
        - derive an abstract class directly from `abc.ABC`, no need for the metaclass
        - sort the list of exported symbols (`__all__`)
        - add an empty line to the end of the "Examples" docstring section
        - push some Ruff configuration settings into the `ruff.lint.*` hierarchy
    - use Pytest 8.x and also install Pygments for syntax highlighting
    - push the unit tests' source from `unit_tests/` into `tests/unit/`
    - also build the documentation in the second Tox stage
    - put the Tox stage specifications in the `pyproject.toml` file on separate lines
    - let `reuse` ignore the `.mypy_cache/` directory, too

## [0.1.7] - 2023-11-08

### Fixes

- Documentation:
    - fix the ReadTheDocs build by adding the `build` section to its configuration

### Additions

- Test suite:
    - also run the Ruff formatter in the `format` Tox check environment
    - add a "reformat-ruff" Tox environment that uses the Ruff formatter
    - add the "reuse" environment to the list of Tox environments to run by
      default and install Git in the Nix derivation since the `reuse` tool
      uses it to figure out which files to check

### Other changes

- Documentation:
    - use mkdocstrings 0.23 with no changes
- Test suite:
    - use Ruff 0.1.4:
        - specify the copyright notice pattern for Ruff to look for
    - let Ruff also reformat the docstrings in addition to the import blocks
    - move the "reuse" Tox test environment to the first (quick) stage

## [0.1.6] - 2023-09-28

### Other changes

- Test suite:
    - use a pinned version of Ruff to avoid breakage with changes enabled in
      future versions
    - use Ruff 0.0.291, add a forgotten deferred annotations import
    - move the "format" check to the first Tox stage
    - use black 23.7 or later so it understands "py312" as a supported version
    - use reuse 2.x with no changes

## [0.1.5] - 2023-06-27

### Fixes

- Build infrastructure:
    - relax the `hatch-requirements-txt` to >= 0.3, which is the version in
      Debian testing/unstable
    - specify a lower requirement for `hatchling` as >= 1.8, which is
      the version in Ubuntu 22.10 (kinetic)
    - specify an upper requirement for `hatchling`
- Main source:
    - do not disable all Flake8 / Ruff checks for three files!
    - fix some formatting nits in the newly-checked source files
- Test suite:
    - drop the `pyupgrade` environment from Tox's default envlist;
      there is (by design) no way to run it in a no-op, report-only mode
    - do not pass the `python_version` option to `mypy`, let it check
      the code with regard to the currently-running Python interpreter

### Additions

- Build infrastructure:
    - specify the project license
    - add some more PyPI trove classifiers
- Test suite:
    - introduce the `PY_MINVER_MIN` and `PY_MINVER_MAX` environment variables for
      the `nix/run-pytest.sh` helper tool so that e.g. the current flakiness of
      Python 3.12 in nixpkgs-unstable can be skipped
    - add a Nix expression and the `nix/run-tox.sh` helper tool to run
      all the Tox tests using a different Python version
    - also include the `reuse` Tox environment in the ones run at the `@check`
      stage using the `tox-stages` tool

### Other changes

- Main source:
    - replace assertions in the parsing code with `if` statements that
      raise our own exceptions
- Documentation:
    - refer to version 1.1.0 of the "Keep a Changelog" format specification
    - use `mkdocstrings` 0.22, no changes
- Test suite:
    - drop the `flake8` / `pep8`, `pylint`, and `pydocstyle`
      Tox test environments, Ruff handles most of these checks now
    - use Ruff 0.0.275, activate all the new check areas, just in case
    - use mypy 1.x, no changes

## [0.1.4] - 2023-05-13

### Additions

- Documentation:
    - add a [ReadTheDocs mirror](https://parse-stages.readthedocs.io/)
- Main source:
    - `parse_stage_ids()`: allow an empty set to be specified by the exact
      strings "", "0", or "none"

### Other changes

- Build system:
    - drop the obsolete `tool.setuptools.*` sections from the `pyproject.toml` file
- Documentation:
    - bump the version of `mkdocstrings-python` with no changes
- Test suite:
    - Ruff:
        - use Ruff 0.0.267, enable the `FLY` checks area

## [0.1.3] - 2023-05-07

### Fixes

- Add a blank line to a docstring section (ruff D214).
- Drop the text in a `NotImplementedError` raised in an abstract method;
  it should be obvious (ruff EM101)

### Additions

- Add a `.gitignore` file, mostly so that `reuse` can be run at any time
- Add a "Home, GitLab, PyPI" navigational line to the documentation
  index page and to the `README.md` file

### Other changes

- Main source:
    - reformat the import sections using Ruff's `isort` implementation
- Build system:
    - switch to `hatch` / `hatchling` for the PEP517 build
- Documentation:
    - use the `default_handler` configuration option of `mkdocstrings`
      instead of specifying `handler: python` for each class!
    - bump the versions of `mkdocstrings` and `mkdocstrings-python` with
      no changes
- Test suite:
    - specify 4.1 as the Tox minimum version and switch to the Tox 4.x
      format for the multiline list of files
    - rename the `black` Tox environment to `format` and
      the `black-reformat` one to `reformat`, since they also run
      Ruff's `isort` now
    - Ruff:
        - use Ruff 0.0.265, enable the `INT` checks area although
          we do not use gettext
        - enable all ruff check areas in `config/ruff-most/`, let
          the `config/ruff-base/` files take care of the ignored ones
        - no longer disable the "relative imports" check, it does not
          complain about our source code
    - Pylint:
        - reenable the "empty comment" plugin; we should have no
          trouble with it since switching to SPDX license tags
    - Bump the versions of `flake8-implicit-str-concat`, `flake8-simplify`,
      `pylint`, and `triceratops` with no code changes

## [0.1.2] - 2023-03-10

### Semi-incompatible changes

- Drop Python 3.7 support.

### Fixes

- Fix the 0.1.1 release URL in the changelog file.
- Do not run the `pyupgrade` Tox environment automatically.
- Add a docstring to the unit test suite's `__init__.py` file instead of
  overriding a linter check.

### Additions

- Start some MkDocs-based documentation.
- Add the `reuse` Tox test environment to run the REUSE tool manually.

### Other changes

- Rework the Ruff invocation Tox targets a bit:
    - drop the `ruff-all-unchained` test environment; at this point in
      Ruff's development we are bound to specific versions anyway
    - move the config files to a `config/` directory, not `.config/`
    - move the "normal" Ruff invocation configuration to `config/ruff-most/`
    - use Ruff 0.0.254 with no code changes
    - activate all of Ruff 0.0.254's liners in the "normal" invocation
- Switch to SPDX license tags.
- Specify the supported Python version in the configuration of the pylint and
  black tools.
- Move the changelog file into the documentation directory.
- In the packaging metadata, point to the Ringlet homepage generated from
  the newly-added documentation.

## [0.1.1] - 2023-02-05

### Fixes

- Use "precedence" instead of "priority" when discussing operators in
  the README file.
- Do not use the `list` generic type in the definition of the `TaggedFrozen` and
  `Tagged` classes; library consumers may try to use `typing.get_type_hints()` on
  them or on derived classes, and Python < 3.9 would have a problem with that.
- Fill in the module docstring using the text of the README file.
- Fix some problems reported by `ruff`:
    - fix the order of some `import` statements
    - fix the formatting of some docstrings

### Other changes

- Add the `ruff-all` test environment that enables all the checks of the `ruff`
  tool for a certain locked version of `ruff`.
- Add the `tool.test-stages` section in the `pyproject.toml` file to specify
  the order that Tox environments should be run during development using
  the `tox-stages` tool from the `test-stages` Python library.
- Add a lot of `flake8` plugins to the Tox `pep8` test environment
- Use ruff 0.0.241, pylint 2.16.x, and black 23.x.

## [0.1.0] - 2023-01-25

### Started

- First public release.

[Unreleased]: https://gitlab.com/ppentchev/parse-stages/-/compare/release%2F0.1.8...main
[0.1.8]: https://gitlab.com/ppentchev/parse-stages/-/compare/release%2F0.1.7...release%2F0.1.8
[0.1.7]: https://gitlab.com/ppentchev/parse-stages/-/compare/release%2F0.1.6...release%2F0.1.7
[0.1.6]: https://gitlab.com/ppentchev/parse-stages/-/compare/release%2F0.1.5...release%2F0.1.6
[0.1.5]: https://gitlab.com/ppentchev/parse-stages/-/compare/release%2F0.1.4...release%2F0.1.5
[0.1.4]: https://gitlab.com/ppentchev/parse-stages/-/compare/release%2F0.1.3...release%2F0.1.4
[0.1.3]: https://gitlab.com/ppentchev/parse-stages/-/compare/release%2F0.1.2...release%2F0.1.3
[0.1.2]: https://gitlab.com/ppentchev/parse-stages/-/compare/release%2F0.1.1...release%2F0.1.2
[0.1.1]: https://gitlab.com/ppentchev/parse-stages/-/compare/release%2F0.1.0...release%2F0.1.1
[0.1.0]: https://gitlab.com/ppentchev/parse-stages/-/tags/release%2F0.1.0
