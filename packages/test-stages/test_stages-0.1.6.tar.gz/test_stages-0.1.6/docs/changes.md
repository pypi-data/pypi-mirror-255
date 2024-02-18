<!--
SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
SPDX-License-Identifier: BSD-2-Clause
-->

# Changelog

All notable changes to the test-stages project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.6] - 2024-02-08

### Additions

- add the `--match-spec` / `-m` command-line option to further limit
  the Tox environments that will be run
- add a Nix expression that builds the documentation
- tentatively declare Python 3.13 as supported
- testing framework:
    - vendor-import [the vetox testing tool](https://devel.ringlet.net/devel/vetox/)
    - add a Nix expression that runs `vetox`

### Other changes

- documentation:
    - use mkdocstrings 0.24 with no changes
- testing framework:
    - use Ruff 0.2.1:
        - push some Ruff configuration settings into the `ruff.lint.*` hierarchy
    - let Ruff insist on trailing commas, reformat the source files accordingly
    - push the unit tests into the `tests/unit/` directory
    - put the Tox stage specifications in the `pyproject.toml` file on separate lines

## [0.1.5] - 2024-01-19

### Fixes

- documentation:
    - add the "build" section to the ReadTheDocs configuration
    - refer to version 1.1.0 of the "Keep a Changelog" specification in
      the changelog file
- selftest:
    - validate the list of archive files before passing it to
      `TarFile.extractall()`

### Additions

- documentation:
    - add a "Download" page linking to the various files at the Ringlet website

### Other changes

- switch from `black` to `ruff` for source code formatting
- documentation:
    - use `mkdocstrings` 0.23 and `mkdocstrings-python` 1.x with no changes
- testing framework:
    - also run the "reuse" test in the first Tox stage
    - also build the documentation in the second Tox stage
    - Ruff:
        - use Ruff 0.1.13
        - disable another subprocess-related check (`S404`)
        - let Ruff also validate the docstrings
    - mypy:
        - do not explicitly install `tomli`, it is brought in as
          a runtime dependency

## [0.1.4] - 2023-10-19

### Fixes

- fix the rendering of long options in the `tox-stages` manual page

### Additions

- tox_trivtags:
    - automatically tell a bootstrapped Tox to install a recent enough version of
      `test-stages` into its own virtual environment so that it may output tags

### Other changes

- drop the documentation section on requiring `test-stages` in the Tox configuration
- build system:
    - refer to Tox 4.x in the "tox" optional dependency group
- selftest:
    - use `pathlib.Path.cwd()` instead of `pathlib.Path().resolve()`
- testing framework:
    - Ruff:
        - use Ruff 0.1.0
        - let it know how to check for our SPDX copyright tags
        - enable its preview mode
    - reuse:
        - use reuse 2.x
        - only run if a Git checkout subdirectory is present
        - with the above in mind, add it to the list of default Tox environments
    - mypy:
        - do not install `tomli` in the virtual environment on recent Python versions

## [0.1.3] - 2023-10-01

### Fixes

- fix a typographical error in the `tox-stages` manual page
- tox_trivtags:
    - fix parsing of the Tox output when the `tox.ini` file contains
      a `min_version` / `minversion` specification and Tox bootstraps a new
      version into a virtual environment:
        - ignore all output lines until one that starts with a `[` character
        - do not depend on the version of Tox that we can see installed as
          a library for determining the format used to output the list of
          tags; a different version may have been installed and invoked
- testing framework:
    - do not pass the `python_version` option to mypy, let it use the current
      interpreter's version for the checks
    - temporarily run `mypy` on `click` version 8.1.3, there seems to be some
      trouble with the decorator changes in 8.1.4

### Additions

- document the `requires` directive that is needed if the `tox.ini` file
  specifies a minimum Tox version requirement

### Other changes

- build system:
    - add Python 3.12 as a supported version
- tox_trivtags:
    - switch from `distlib` to `importlib.metadata` and `packaging` for simpler
      handling
- testing framework:
    - pin the Ruff version to avoid breakage with new checks enabled in the future
    - use Ruff 0.0.291, do not pass the current directory to the `pathlib.Path`
      constructor
    - use black 23.7 and add "py312" to the list of target versions
    - drop the `pylint` test environment, we depend on Ruff instead
    - run the `format` test environment in the first Tox stage

## [0.1.2] - 2023-03-13

### Incompatible changes

- tox-trivtags:
    - drop the `tox_trivtags.parse.parse_config()` function, running
      `tox --showconfig` is the only supported method now

### Fixes

- tox-stages:
    - minor refactoring and fixes suggested by Ruff
- tox-trivtags:
    - use the correct way to ignore a specific Ruff check for the whole
      file instead of telling Ruff to skip that file entirely!
    - minor fixes suggested by Ruff
- testing framework:
    - correct the `tox.envlist` list in the `tox.ini` file

### Additions

- add the beginnings of [MkDocs-based][tool-mkdocs] documentation, hosted
  [at the Ringlet test-stages webpage][ringlet-test-stages]
  for the latest release and [at ReadTheDocs][readthedocs] for
  the latest version from the Git repository
- add manual page for the `tox-stages` tool in the mdoc format
- add a `.gitignore` file, mainly so that the `reuse` tool can be run even
  in the presence of some test-related files and directories
- add a `selftest` module (not installed in the wheel) that runs
  the `tox-stages` tool itself on a copy of the source tree
- build system:
    - add the "Typing :: Typed" PyPI trove classifier
    - specify the project's two-clause BSD license
- tox-stages:
    - add support for Tox 4.x
    - allow the `tox-stages` command-line tool to be invoked via `python3 -m`
    - add the `--arg` / `-A` option to pass additional arguments to Tox
    - add the `--parallel` / `-p` option to specify which stages should run
      their tests in parallel
- testing framework:
    - add the `reuse` Tox test environment for checking the SPDX tags manually

### Other changes

- use SPDX license tags
- move the changelog file into the MkDocs-managed `docs/` directory
- point to the Ringlet homepage in the package metadata and the README file
- tox-stages:
    - reformat the import statements using Ruff's isort implementation
    - use `tox run-parallel` when running with Tox 4.x
- tox-trivtags:
    - reformat the import statements using Ruff's isort implementation
    - use `tox config` when running with Tox 4.x
- build system:
    - switch to hatch/hatchling for the PEP517 build
    - move the `contextlib-chdir` module from the installation requirements to
      the test ones, since we do not use it in the installed library
    - bump the `parse-stages` dependency version to 0.1.4 so that an empty
      set may be specified as an argument to the `--parallel` option
- testing framework:
    - Ruff:
        - move the Ruff configuration files from `.config/` to `config/`
        - run `ruff check ...` explicitly
        - enable all of the Ruff checks in the default (`ruff`) test environment
        - use ruff 0.0.265 and ignore some subprocess checks: we do check
        - remove them `EM` checks override, we do not raise any exceptions
    - Formatting:
        - rename the `black` and `black-reformat` Tox environments to
          `format` and `reformat` respectively and invoke Ruff's isort
          implementation in both
        - specify Python 3.8 as the target version
    - Pylint:
        - remove the `empty-comment` plugin override, the SPDX license tags
          no longer cause it to complain
        - specify Python 3.8 as the target version
        - use pylint 2.17.x with no changes
    - update the `tox.ini` file for Tox 4.x (mostly a multiline list) and
      make the unit tests that run Tox 3.x revert those adaptations
    - use the `@manual` tag for Tox test environments that should only be
      run manually with care
    - drop the Tox environment that runs `flake8` and `pycodestyle`,
      we depend on Ruff for that

## [0.1.1] - 2023-02-07

### Fixes

- Include the changelog file and the `.config/ruff-*/pyproject.toml` files in
  the PyPI source distribution tarball.

## [0.1.0] - 2023-02-07

### Started

- First public release.

[readthedocs]: https://test-stages.readthedocs.io/en/latest/
[ringlet-test-stages]: https://devel.ringlet.net/devel/test-stages/ "The Ringlet test-stages homepage"
[tool-mkdocs]: https://www.mkdocs.org/ "Project documentation with Markdown"

[Unreleased]: https://gitlab.com/ppentchev/test-stages/-/compare/release%2F0.1.6...main
[0.1.6]: https://gitlab.com/ppentchev/test-stages/-/compare/release%2F0.1.5...release%2F0.1.6
[0.1.5]: https://gitlab.com/ppentchev/test-stages/-/compare/release%2F0.1.4...release%2F0.1.5
[0.1.4]: https://gitlab.com/ppentchev/test-stages/-/compare/release%2F0.1.3...release%2F0.1.4
[0.1.3]: https://gitlab.com/ppentchev/test-stages/-/compare/release%2F0.1.2...release%2F0.1.3
[0.1.2]: https://gitlab.com/ppentchev/test-stages/-/compare/release%2F0.1.1...release%2F0.1.2
[0.1.1]: https://gitlab.com/ppentchev/test-stages/-/compare/release%2F0.1.0...release%2F0.1.1
[0.1.0]: https://gitlab.com/ppentchev/test-stages/-/tags/release%2F0.1.0
