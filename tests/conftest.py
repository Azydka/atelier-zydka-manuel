from __future__ import annotations

import json

import pytest

from tests.snapshot import REFERENCE_PATH, build_snapshot


@pytest.fixture(scope="session")
def demo_build(tmp_path_factory):
    snapshot, duration = build_snapshot(tmp_path_factory.mktemp("demo"))
    return {"snapshot": snapshot, "duration": duration}


@pytest.fixture(scope="session")
def reference():
    return json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))
