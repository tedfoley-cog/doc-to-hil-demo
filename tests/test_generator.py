"""Tests for HIL/SIL test generation."""

from __future__ import annotations

from pathlib import Path

from comprehension.knowledge_graph import build_knowledge_graph
from generators.test_generator import generate_tests_from_graph
from parsers.orchestrator import run_all_parsers


def test_generate_tests(source_dir: Path) -> None:
    inventory = run_all_parsers(source_dir)
    graph = build_knowledge_graph(inventory)
    tests = generate_tests_from_graph(graph)

    assert len(tests) > 0
    for test in tests:
        assert test.test_id.startswith("TEST-SM-")
        assert len(test.steps) >= 2


def test_generated_tests_have_signals(source_dir: Path) -> None:
    inventory = run_all_parsers(source_dir)
    graph = build_knowledge_graph(inventory)
    tests = generate_tests_from_graph(graph)

    for test in tests:
        assert len(test.signals) > 0
        signal_names = {s.name for s in test.signals}
        assert "PowerModeState" in signal_names
