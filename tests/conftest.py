"""Shared fixtures for tests."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def source_dir() -> Path:
    """Path to source documents directory."""
    return Path(__file__).parent.parent / "source_documents"


@pytest.fixture
def traces_dir() -> Path:
    """Path to SIL trace files."""
    return Path(__file__).parent.parent / "sil_harness" / "traces"
