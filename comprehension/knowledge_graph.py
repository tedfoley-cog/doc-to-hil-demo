"""Build a knowledge graph from parsed document entities."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

from parsers.models import DocumentInventory, EntityType
from parsers.orchestrator import run_all_parsers


@dataclass
class GraphNode:
    """A node in the knowledge graph."""

    node_id: str
    node_type: str
    label: str
    properties: dict[str, object] = field(default_factory=dict)
    source_document: str = ""


@dataclass
class GraphEdge:
    """An edge in the knowledge graph."""

    source: str
    target: str
    edge_type: str
    properties: dict[str, object] = field(default_factory=dict)


@dataclass
class KnowledgeGraph:
    """In-memory knowledge graph connecting all extracted entities."""

    nodes: dict[str, GraphNode] = field(default_factory=dict)
    edges: list[GraphEdge] = field(default_factory=list)

    def add_node(self, node: GraphNode) -> None:
        self.nodes[node.node_id] = node

    def add_edge(self, edge: GraphEdge) -> None:
        self.edges.append(edge)

    def get_neighbors(self, node_id: str) -> list[str]:
        """Get all nodes connected to the given node."""
        neighbors: list[str] = []
        for edge in self.edges:
            if edge.source == node_id:
                neighbors.append(edge.target)
            elif edge.target == node_id:
                neighbors.append(edge.source)
        return neighbors

    def get_nodes_by_type(self, node_type: str) -> list[GraphNode]:
        return [n for n in self.nodes.values() if n.node_type == node_type]

    def get_edges_from(self, node_id: str) -> list[GraphEdge]:
        return [e for e in self.edges if e.source == node_id]

    def summary(self) -> dict[str, object]:
        type_counts: dict[str, int] = {}
        for node in self.nodes.values():
            type_counts[node.node_type] = type_counts.get(node.node_type, 0) + 1
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "nodes_by_type": type_counts,
        }


def build_knowledge_graph(inventory: DocumentInventory) -> KnowledgeGraph:
    """Build a knowledge graph from the document inventory."""
    graph = KnowledgeGraph()

    for doc in inventory.documents:
        doc_node = GraphNode(
            node_id=doc.document_id,
            node_type="document",
            label=doc.title,
            properties={"type": doc.doc_type.value, "revision": doc.revision},
        )
        graph.add_node(doc_node)

        for entity in doc.entities:
            node = GraphNode(
                node_id=entity.entity_id,
                node_type=entity.entity_type.value,
                label=entity.label,
                properties=entity.properties,
                source_document=doc.document_id,
            )
            graph.add_node(node)

            graph.add_edge(
                GraphEdge(
                    source=doc.document_id,
                    target=entity.entity_id,
                    edge_type="contains",
                )
            )

    _link_transitions_to_states(graph)
    _link_dtcs_to_requirements(graph, inventory)
    _link_dtcs_to_signals(graph, inventory)
    _link_requirements_to_signals(graph, inventory)

    return graph


def _link_transitions_to_states(graph: KnowledgeGraph) -> None:
    """Link transition nodes to their source and target states."""
    transitions = graph.get_nodes_by_type("transition")
    states = {n.node_id: n for n in graph.get_nodes_by_type("state")}

    for trans in transitions:
        parts = trans.node_id.split("->")
        if len(parts) == 2:
            from_state = parts[0].strip()
            to_state = parts[1].strip()
            if from_state in states:
                graph.add_edge(
                    GraphEdge(source=from_state, target=trans.node_id, edge_type="exits")
                )
            if to_state in states:
                graph.add_edge(
                    GraphEdge(source=trans.node_id, target=to_state, edge_type="enters")
                )


def _link_dtcs_to_requirements(
    graph: KnowledgeGraph, inventory: DocumentInventory
) -> None:
    """Link DTCs to related requirements via cross-reference data."""
    for doc in inventory.documents:
        for entity in doc.entities:
            if entity.entity_type != EntityType.DTC:
                continue
            dtc_code = entity.entity_id
            for rel in entity.relationships:
                if rel.relationship_type == "related_requirement":
                    graph.add_edge(
                        GraphEdge(
                            source=dtc_code,
                            target=rel.target_id,
                            edge_type="tests_requirement",
                        )
                    )


def _link_dtcs_to_signals(
    graph: KnowledgeGraph, inventory: DocumentInventory
) -> None:
    """Link DTCs to related CAN signals via inventory relationships."""
    signal_nodes = {n.node_id: n for n in graph.get_nodes_by_type("signal")}

    for doc in inventory.documents:
        for entity in doc.entities:
            if entity.entity_type != EntityType.DTC:
                continue
            dtc_code = entity.entity_id
            for rel in entity.relationships:
                if rel.relationship_type == "related_signal" and rel.target_id in signal_nodes:
                    graph.add_edge(
                        GraphEdge(
                            source=dtc_code,
                            target=rel.target_id,
                            edge_type="monitors_signal",
                        )
                    )


def _link_requirements_to_signals(
    graph: KnowledgeGraph, inventory: DocumentInventory
) -> None:
    """Link requirements to signals they reference."""
    _dummy = inventory
    req_nodes = graph.get_nodes_by_type("requirement")
    signal_nodes = graph.get_nodes_by_type("signal")

    signal_keywords: dict[str, str] = {}
    for sig in signal_nodes:
        keywords = sig.label.lower().replace("_", " ").split()
        for kw in keywords:
            if len(kw) > 3:
                signal_keywords[kw] = sig.node_id

    for req in req_nodes:
        text_lower = req.label.lower()
        for kw, sig_id in signal_keywords.items():
            if kw in text_lower:
                graph.add_edge(
                    GraphEdge(
                        source=req.node_id,
                        target=sig_id,
                        edge_type="references_signal",
                    )
                )


def export_graph_json(graph: KnowledgeGraph, output_path: Path) -> None:
    """Export the knowledge graph to JSON for the dashboard."""
    data = {
        "summary": graph.summary(),
        "nodes": [
            {
                "id": n.node_id,
                "type": n.node_type,
                "label": n.label,
                "properties": n.properties,
                "source_document": n.source_document,
            }
            for n in graph.nodes.values()
        ],
        "edges": [
            {
                "source": e.source,
                "target": e.target,
                "type": e.edge_type,
            }
            for e in graph.edges
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Knowledge graph exported to {output_path}")
    summary = graph.summary()
    print(f"  Nodes: {summary['total_nodes']}, Edges: {summary['total_edges']}")
    nodes_by_type: dict[str, int] = {}
    raw = summary.get("nodes_by_type", {})
    if isinstance(raw, dict):
        nodes_by_type = {str(k): int(v) for k, v in raw.items()}
    for t, c in nodes_by_type.items():
        print(f"    {t}: {c}")


def main() -> None:
    """CLI entrypoint: build knowledge graph and export."""
    source_dir = Path("source_documents")
    if len(sys.argv) > 1:
        source_dir = Path(sys.argv[1])

    inventory = run_all_parsers(source_dir)
    graph = build_knowledge_graph(inventory)
    export_graph_json(graph, Path("dashboard") / "knowledge_graph.json")


if __name__ == "__main__":
    main()
