# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause
"""Parse a list of tags in the Tox configuration.

Inspired by https://github.com/tox-dev/tox-tags
"""

from __future__ import annotations

import importlib.metadata
import typing

import packaging.version as pver


if typing.TYPE_CHECKING:
    from typing import Final


def _get_tox_version() -> str | None:
    """Figure out which version of Tox is installed."""
    try:
        dist: Final = importlib.metadata.metadata("tox")
    except ModuleNotFoundError:
        return None

    return dist.get("Version")


_TOX_VERSION: Final = _get_tox_version()

if _TOX_VERSION is None:
    HAVE_MOD_TOX_3 = False
    HAVE_MOD_TOX_4 = False
else:
    HAVE_MOD_TOX_3 = pver.Version("3") <= pver.Version(_TOX_VERSION) < pver.Version("4")

    HAVE_MOD_TOX_4 = pver.Version("4") <= pver.Version(_TOX_VERSION) < pver.Version("5")


if HAVE_MOD_TOX_3:
    import tox
    import tox.config

    @tox.hookimpl
    def tox_addoption(parser: tox.config.Parser) -> None:
        """Parse a testenv's "tags" attribute as a list of lines."""
        parser.add_testenv_attribute(
            "tags",
            "line-list",
            "A list of tags describing this test environment",
            default=[],
        )


if HAVE_MOD_TOX_4:
    from typing import List

    import tox.plugin as t_plugin

    if typing.TYPE_CHECKING:
        import tox.config.sets as t_sets
        import tox.session.state as t_state

    @t_plugin.impl
    def tox_add_env_config(
        env_conf: t_sets.EnvConfigSet,
        state: t_state.State,  # noqa: ARG001
    ) -> None:
        """Parse a testenv's "tags" attribute as a list of lines."""
        env_conf.add_config(
            keys=["tags"],
            of_type=List[str],
            default=[],
            desc="A list of tags describing this test environment",
        )
