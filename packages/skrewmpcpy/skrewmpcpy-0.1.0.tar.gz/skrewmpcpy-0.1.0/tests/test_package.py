from __future__ import annotations

import importlib.metadata

import skrewmpcpy as m


def test_version():
    assert importlib.metadata.version("skrewmpcpy") == m.__version__
