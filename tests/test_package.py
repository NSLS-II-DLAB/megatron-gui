from __future__ import annotations

import importlib.metadata

import megatron_gui as m


def test_version():
    assert importlib.metadata.version("megatron_gui") == m.__version__
