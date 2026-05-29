"""Generate HIL/SIL test scripts from the knowledge graph."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from comprehension.knowledge_graph import KnowledgeGraph, build_knowledge_graph
from parsers.orchestrator import run_all_parsers


@dataclass
class HILSignal:
    """A signal used in a test step."""

    name: str
    initial_value: float | int | str = 0


@dataclass
class HILStep:
    """A single step in a test procedure."""

    description: str
    stimulus: dict[str, float | int | str] = field(default_factory=dict)
    expected: dict[str, float | int | str] = field(default_factory=dict)


@dataclass
class GeneratedTest:
    """A complete generated test case."""

    test_id: str
    requirement_id: str
    requirement_text: str
    source_document: str
    signals: list[HILSignal] = field(default_factory=list)
    steps: list[HILStep] = field(default_factory=list)


def generate_tests_from_graph(graph: KnowledgeGraph) -> list[GeneratedTest]:
    """Generate test cases from knowledge graph state machine transitions."""
    tests: list[GeneratedTest] = []
    transitions = graph.get_nodes_by_type("transition")

    for i, trans in enumerate(transitions):
        parts = trans.node_id.split("->")
        if len(parts) != 2:
            continue

        from_state = parts[0].strip()
        to_state = parts[1].strip()
        condition = str(trans.properties.get("condition", ""))
        guard = str(trans.properties.get("guard", "") or "")

        test_id = f"TEST-SM-{i + 1:03d}"
        req_text = f"Verify transition {from_state} -> {to_state} when {condition}"

        related_reqs = _find_related_requirements(graph, trans.node_id)
        req_id = related_reqs[0] if related_reqs else f"TRANS-{from_state}-{to_state}"

        signals = [
            HILSignal(name="PowerModeState", initial_value=0),
            HILSignal(name="IgnitionSwitch", initial_value=0),
            HILSignal(name="BatteryVoltage", initial_value=12.0),
            HILSignal(name="EngineRPM", initial_value=0),
        ]

        steps = [
            HILStep(
                description=f"Set initial state: {from_state}",
                stimulus={"PowerModeState": _state_code(from_state)},
                expected={"PowerModeState": _state_code(from_state)},
            ),
            HILStep(
                description=f"Apply condition: {condition}",
                stimulus=_parse_condition_stimulus(condition),
                expected={},
            ),
        ]

        if guard:
            steps.append(
                HILStep(
                    description=f"Verify guard: {guard}",
                    stimulus=_parse_condition_stimulus(guard),
                    expected={},
                )
            )

        steps.append(
            HILStep(
                description=f"Verify transition to {to_state}",
                stimulus={},
                expected={"PowerModeState": _state_code(to_state)},
            )
        )

        tests.append(
            GeneratedTest(
                test_id=test_id,
                requirement_id=req_id,
                requirement_text=req_text,
                source_document=trans.source_document,
                signals=signals,
                steps=steps,
            )
        )

    return tests


def _find_related_requirements(graph: KnowledgeGraph, entity_id: str) -> list[str]:
    """Find requirements related to an entity via graph edges."""
    reqs: list[str] = []
    for edge in graph.edges:
        if edge.source == entity_id and edge.edge_type == "tests_requirement":
            reqs.append(edge.target)
        if edge.target == entity_id and edge.edge_type == "tests_requirement":
            reqs.append(edge.source)
    return reqs


def _state_code(state_name: str) -> int:
    """Map state name to numeric code."""
    codes = {
        "OFF": 0, "ACC": 1, "RUN": 2, "CRANK": 3,
        "RUN_ENGINE": 4, "EMERGENCY_STOP": 5,
        "P": 0, "R": 1, "N": 2, "D": 3,
    }
    return codes.get(state_name, 0)


def _parse_condition_stimulus(condition: str) -> dict[str, float | int | str]:
    """Parse a condition string into stimulus signal values."""
    stimulus: dict[str, float | int | str] = {}
    if "IGN_SW" in condition:
        if "ACC" in condition:
            stimulus["IgnitionSwitch"] = 1
        elif "RUN" in condition:
            stimulus["IgnitionSwitch"] = 2
        elif "OFF" in condition:
            stimulus["IgnitionSwitch"] = 0
    if "START_REQ" in condition:
        stimulus["StartRequest"] = 1
    if "ENGINE_RPM" in condition:
        stimulus["EngineRPM"] = 800
    if "FAULT_CRITICAL" in condition:
        stimulus["FaultCritical"] = 1
    if "BATT_V" in condition:
        stimulus["BatteryVoltage"] = 12.5
    if "TRANS_RANGE" in condition:
        stimulus["TransRange"] = 0  # PARK
    if "OIL_PRESS" in condition:
        stimulus["OilPressure"] = 25
    if "brake" in condition.lower():
        stimulus["BrakePedal"] = 1
    if "speed" in condition.lower():
        stimulus["VehicleSpeed"] = 0
    return stimulus


def render_test_scripts(
    tests: list[GeneratedTest], output_dir: Path, template_dir: Path | None = None
) -> list[Path]:
    """Render test cases to Python script files using Jinja2 template."""
    if template_dir is None:
        template_dir = Path("generators/templates")

    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("hil_test_template.py.j2")

    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for test in tests:
        content = template.render(
            test_id=test.test_id,
            requirement_id=test.requirement_id,
            requirement_text=test.requirement_text,
            source_document=test.source_document,
            signals=test.signals,
            steps=test.steps,
        )
        filename = f"{test.test_id.lower().replace('-', '_')}.py"
        out_path = output_dir / filename
        with open(out_path, "w") as f:
            f.write(content)
        written.append(out_path)

    return written


def main() -> None:
    """CLI entrypoint: generate test scripts from knowledge graph."""
    source_dir = Path("source_documents")
    if len(sys.argv) > 1:
        source_dir = Path(sys.argv[1])

    output_dir = Path("hil_output/generated")

    inventory = run_all_parsers(source_dir)
    graph = build_knowledge_graph(inventory)
    tests = generate_tests_from_graph(graph)

    print(f"Generated {len(tests)} test cases from knowledge graph")

    written = render_test_scripts(tests, output_dir)
    print(f"Wrote {len(written)} test scripts to {output_dir}")

    manifest = {
        "total_tests": len(tests),
        "tests": [
            {
                "test_id": t.test_id,
                "requirement_id": t.requirement_id,
                "description": t.requirement_text,
                "steps": len(t.steps),
            }
            for t in tests
        ],
    }
    manifest_path = Path("dashboard") / "test_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"Test manifest written to {manifest_path}")


if __name__ == "__main__":
    main()
