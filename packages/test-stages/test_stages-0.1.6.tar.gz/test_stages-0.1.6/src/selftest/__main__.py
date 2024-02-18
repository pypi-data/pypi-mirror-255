# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Run a test for the `test-stages` library's `tox-stages` runner."""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import tarfile
import tempfile
import typing

import pyproject_hooks
import tomli_w
import utf8_locale


if sys.version_info >= (3, 11):
    import contextlib as contextlib_chdir

    import tomllib
else:
    import contextlib_chdir
    import tomli as tomllib


if typing.TYPE_CHECKING:
    from typing import Final


def validate_srcdir(srcdir: pathlib.Path) -> None:
    """Make sure we can find a couple of files in the source directory."""
    for relpath in (
        "requirements/install.txt",
        "src/test_stages/tox_stages/__main__.py",
        "tests/unit/test_functional.py",
    ):
        path = srcdir / relpath
        if not path.is_file():
            sys.exit(f"Expected to find {relpath} in {srcdir}, but {path} is not a regular file")


def build_sdist(srcdir: pathlib.Path, tempd: pathlib.Path) -> pathlib.Path:
    """Build a source distribution tarball."""
    with contextlib_chdir.chdir(tempd):
        distdir: Final = tempd / "dist"
        distdir.mkdir(mode=0o755)

        backend: Final = tomllib.loads((srcdir / "pyproject.toml").read_text(encoding="UTF-8"))[
            "build-system"
        ]["build-backend"]

        caller: Final = pyproject_hooks.BuildBackendHookCaller(srcdir, backend)
        fname: Final = caller.build_sdist(distdir)
        sdist: Final = distdir / fname
        if sdist.parent != distdir:
            sys.exit(f"The PEP517 build returned {fname} which does not seem to be a pure filename")
        return sdist


def safe_extract_all(star: tarfile.TarFile, topdir: pathlib.Path) -> None:
    """Validate the member names in the archive and extract them all."""
    members: Final = star.getmembers()
    paths: Final = [pathlib.Path(member.name) for member in members]
    if not paths:
        sys.exit("Expected at least one member in the source archive")
    if paths[0].is_absolute():
        sys.exit(f"Did not expect an absolute path {paths[0]} in the source archive")

    base_path: Final = paths[0].parts[0]
    bad_paths: Final = [path for path in paths if path.parts[0] != base_path]
    if bad_paths:
        sys.exit(
            f"Bad paths in the source archive, expected all of them to "
            f"start with {base_path}: {bad_paths}",
        )

    bad_dirs: Final = [path for path in paths if ".." in path.parts]
    if bad_dirs:
        sys.exit(f"Bad paths in the source archive, none of them should contain '..': {bad_paths}")

    star.extractall(topdir, members=members)  # noqa: S202


def extract_sdist(sdist: pathlib.Path, tempd: pathlib.Path) -> pathlib.Path:
    """Extract the sdist tarball."""
    if not sdist.name.endswith(".tar.gz"):
        sys.exit(f"The PEP517 build generated a non-.tar.gz file: {sdist}")

    topdir: Final = tempd / "src"
    topdir.mkdir(mode=0o755)

    with tarfile.open(sdist, mode="r") as star:
        safe_extract_all(star, topdir)
        entries: Final = sorted(path for path in topdir.iterdir())
        if len(entries) != 1:
            sys.exit(f"Expected {sdist} to contain a single directory, got {entries!r}")

    testdir: Final = entries[0]
    if not testdir.is_dir() or not testdir.name.startswith(("test_stages-", "test-stages-")):
        sys.exit(f"Expected {sdist} to contain a single `test-stages-*` directory, got {testdir}")
    return testdir


def adapt_pyproject(testdir: pathlib.Path) -> None:
    """Disable this selftest to avoid infinite recursion."""
    projfile: Final = testdir / "pyproject.toml"
    projdata: Final = tomllib.loads(projfile.read_text(encoding="UTF-8"))

    stages: Final = projdata["tool"]["test-stages"]["stages"]
    if not stages[-1].startswith("@tests"):
        sys.exit(f"Expected a `@tests...` test-stages entry, got {stages!r}")
    stages[-1] = f"{stages[-1]} and not selftest"

    projfile.write_text(tomli_w.dumps(projdata), encoding="UTF-8")


def run_tox(testdir: pathlib.Path) -> None:
    """Clean up the environment a bit, then run Tox."""
    env: Final = dict(item for item in os.environ.items() if not item[0].startswith("TOX"))
    subprocess.check_call(["pwd"], cwd=testdir, env=env)
    subprocess.check_call(["cat", "pyproject.toml"], cwd=testdir, env=env)

    subprocess.check_call(["tox-stages", "available"], cwd=testdir, env=env)

    marker: Final = testdir / "selftest-marker.txt"
    if marker.is_symlink() or marker.exists():
        sys.exit(f"Did not expect {marker} to exist")
    subprocess.check_call(
        ["python3", "-m", "test_stages.tox_stages", "run", "@selftest"],
        cwd=testdir,
        env=env,
    )
    if not marker.is_file():
        sys.exit(f"`tox-stages run @selftest` did not create {marker}")

    marker.unlink()
    subprocess.check_call(
        ["python3", "-m", "test_stages.tox_stages", "run", "--arg", "--notest", "@selftest"],
        cwd=testdir,
        env=env,
    )
    if marker.is_symlink() or marker.exists():
        sys.exit(f"A `--notest` run still created {marker}")

    subprocess.check_call(
        ["python3", "-m", "test_stages.tox_stages", "run", "(@docs or not @manual) and @selftest"],
        cwd=testdir,
        env=env,
    )
    if not marker.is_file():
        sys.exit(f"`tox-stages run (@docs or not @manual) and @selftest` did not create {marker}")

    marker.unlink()
    subprocess.check_call(
        ["python3", "-m", "test_stages.tox_stages", "run", "-m", "@selftest", "not @manual"],
        cwd=testdir,
        env=env,
    )
    if not marker.is_file():
        sys.exit(f"`tox-stages run -m @selftest not @manual` did not create {marker}")

    utf8_env = dict(env)
    utf8_env.update(utf8_locale.UTF8Detect().detect().env_vars)
    blurb = "import pathlib"
    if blurb in subprocess.check_output(
        ["tox-stages", "run", "@selftest"],
        cwd=testdir,
        encoding="UTF-8",
        env=utf8_env,
    ):
        sys.exit("A run without any -p option output {blurb!r}")

    if blurb in subprocess.check_output(
        ["tox-stages", "run", "@selftest", "-p", "1"],
        cwd=testdir,
        encoding="UTF-8",
        env=utf8_env,
    ):
        sys.exit("A `-p 1` run did not output {blurb!r}")

    if blurb not in subprocess.check_output(
        ["tox-stages", "run", "@selftest", "-p", "7"],
        cwd=testdir,
        encoding="UTF-8",
        env=utf8_env,
    ):
        sys.exit("A `-p 7` run output {blurb!r}")

    subprocess.check_call(["tox-stages", "run"], cwd=testdir, env=env)


def main() -> None:
    """Build a source distribution, extract it, run some tests."""
    srcdir: Final = pathlib.Path.cwd()
    validate_srcdir(srcdir)

    with tempfile.TemporaryDirectory() as tempd_name:
        tempd: Final = pathlib.Path(tempd_name)
        sdist: Final = build_sdist(srcdir, tempd)
        testdir: Final = extract_sdist(sdist, tempd)
        adapt_pyproject(testdir)
        run_tox(testdir)


if __name__ == "__main__":
    main()
