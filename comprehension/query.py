"""Query the knowledge graph for impact analysis and test coverage."""

from __future__ import annotations

from comprehension.knowledge_graph import KnowledgeGraph


def find_impact(graph: KnowledgeGraph, changed_entity_id: str) -> list[str]:
    """Find all entities impacted by a change to the given entity.

    Performs a breadth-first traversal from the changed entity, following
    edges in both directions, to find all connected entities that would
    need review or re-testing.
    """
    visited: set[str] = set()
    queue = [changed_entity_id]
    impacted: list[str] = []

    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)
        if current != changed_entity_id:
            impacted.append(current)

        neighbors = graph.get_neighbors(current)
        for n in neighbors:
            if n not in visited:
                queue.append(n)

    return impacted


def find_untested_requirements(graph: KnowledgeGraph) -> list[str]:
    """Find requirements that have no associated test coverage.

    A requirement is considered 'tested' if it has an edge of type
    'tests_requirement' from a DTC or test entity pointing to it.
    """
    requirements = graph.get_nodes_by_type("requirement")
    tested: set[str] = set()

    for edge in graph.edges:
        if edge.edge_type in ("tests_requirement", "verified_by"):
            tested.add(edge.target)

    return [r.node_id for r in requirements if r.node_id not in tested]


def find_signals_for_requirement(graph: KnowledgeGraph, req_id: str) -> list[str]:
    """Find all CAN signals referenced by a requirement."""
    signals: list[str] = []
    for edge in graph.edges:
        if edge.source == req_id and edge.edge_type == "references_signal":
            signals.append(edge.target)
    return signals


def get_state_machine_coverage(graph: KnowledgeGraph) -> dict[str, object]:
    """Compute coverage metrics for state machine transitions."""
    states = graph.get_nodes_by_type("state")
    transitions = graph.get_nodes_by_type("transition")

    states_with_exit = set()
    states_with_entry = set()
    for t in transitions:
        parts = t.node_id.split("->")
        if len(parts) == 2:
            states_with_exit.add(parts[0].strip())
            states_with_entry.add(parts[1].strip())

    state_ids = {s.node_id for s in states}
    dead_states = state_ids - states_with_exit - states_with_entry

    return {
        "total_states": len(states),
        "total_transitions": len(transitions),
        "states_with_exit_transition": len(states_with_exit),
        "states_with_entry_transition": len(states_with_entry),
        "dead_states": list(dead_states),
    }
