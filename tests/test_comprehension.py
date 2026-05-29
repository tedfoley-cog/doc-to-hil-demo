"""Tests for knowledge graph construction and querying."""

from __future__ import annotations

from pathlib import Path

from comprehension.knowledge_graph import build_knowledge_graph
from comprehension.query import (
    find_impact,
    find_signals_for_requirement,
    find_untested_requirements,
    get_state_machine_coverage,
)
from parsers.orchestrator import run_all_parsers


def test_build_knowledge_graph(source_dir: Path) -> None:
    inventory = run_all_parsers(source_dir)
    graph = build_knowledge_graph(inventory)

    assert len(graph.nodes) > 0
    assert len(graph.edges) > 0

    doc_nodes = graph.get_nodes_by_type("document")
    assert len(doc_nodes) >= 4

    state_nodes = graph.get_nodes_by_type("state")
    assert len(state_nodes) >= 6


def test_find_impact(source_dir: Path) -> None:
    inventory = run_all_parsers(source_dir)
    graph = build_knowledge_graph(inventory)

    impacted = find_impact(graph, "OFF")
    assert len(impacted) > 0


def test_find_untested_requirements(source_dir: Path) -> None:
    inventory = run_all_parsers(source_dir)
    graph = build_knowledge_graph(inventory)

    untested = find_untested_requirements(graph)
    assert isinstance(untested, list)


def test_find_signals_for_requirement(source_dir: Path) -> None:
    inventory = run_all_parsers(source_dir)
    graph = build_knowledge_graph(inventory)

    signals = find_signals_for_requirement(graph, "REQ-PM-001")
    assert isinstance(signals, list)


def test_state_machine_coverage(source_dir: Path) -> None:
    inventory = run_all_parsers(source_dir)
    graph = build_knowledge_graph(inventory)

    coverage = get_state_machine_coverage(graph)
    total_states = coverage["total_states"]
    total_transitions = coverage["total_transitions"]
    assert isinstance(total_states, int) and total_states >= 6
    assert isinstance(total_transitions, int) and total_transitions >= 10
