"""Parse PDF specification documents (via pre-extracted JSON)."""

from __future__ import annotations

import json
from pathlib import Path

from parsers.models import (
    CANSignal,
    DocumentType,
    FlowStep,
    ParsedDocument,
    Requirement,
    State,
    Transition,
)


def parse_pdf_spec(extracted_json_path: Path) -> ParsedDocument:
    """Parse a PDF spec from its pre-extracted JSON representation.

    In production, this would use PyMuPDF + Camelot for tables and a vision
    model for state machine / flow diagram extraction. The demo uses
    pre-extracted JSON that represents what those tools would produce.
    """
    with open(extracted_json_path) as f:
        data = json.load(f)

    doc = ParsedDocument(
        document_id=data["document_id"],
        title=data["title"],
        doc_type=DocumentType.PDF_SPEC,
        source_path=str(extracted_json_path),
        revision=data.get("revision", ""),
        subsystem=data.get("subsystem", ""),
        asil=data.get("asil", "QM"),
    )

    return doc


def extract_states(data: dict[str, object]) -> list[State]:
    """Extract state machine states from parsed PDF data."""
    states: list[State] = []
    sm = data.get("state_machine")
    if not isinstance(sm, dict):
        return states

    raw_states = sm.get("states")
    if not isinstance(raw_states, list):
        return states

    doc_id = data.get("document_id", "")
    if not isinstance(doc_id, str):
        doc_id = ""

    for s in raw_states:
        if not isinstance(s, dict):
            continue
        states.append(
            State(
                state_id=str(s.get("id", "")),
                name=str(s.get("id", "")),
                code=str(s.get("code", "")),
                description=str(s.get("description", "")),
                document_id=doc_id,
            )
        )
    return states


def extract_transitions(data: dict[str, object]) -> list[Transition]:
    """Extract state machine transitions from parsed PDF data."""
    transitions: list[Transition] = []
    sm = data.get("state_machine")
    if not isinstance(sm, dict):
        gsm = data.get("gear_range_state_machine")
        if isinstance(gsm, dict):
            raw_trans = gsm.get("transitions")
            if isinstance(raw_trans, list):
                doc_id = data.get("document_id", "")
                if not isinstance(doc_id, str):
                    doc_id = ""
                for t in raw_trans:
                    if not isinstance(t, dict):
                        continue
                    transitions.append(
                        Transition(
                            from_state=str(t.get("from", "")),
                            to_state=str(t.get("to", "")),
                            condition=str(t.get("condition", "")),
                            document_id=doc_id,
                        )
                    )
        return transitions

    raw_trans = sm.get("transitions")
    if not isinstance(raw_trans, list):
        return transitions

    doc_id = data.get("document_id", "")
    if not isinstance(doc_id, str):
        doc_id = ""

    for t in raw_trans:
        if not isinstance(t, dict):
            continue
        timeout_raw = t.get("timeout_ms")
        timeout_ms = int(timeout_raw) if timeout_raw is not None else None
        transitions.append(
            Transition(
                from_state=str(t.get("from", "")),
                to_state=str(t.get("to", "")),
                condition=str(t.get("condition", "")),
                guard=str(t.get("guard", "") or ""),
                timeout_ms=timeout_ms,
                document_id=doc_id,
            )
        )
    return transitions


def extract_requirements_from_pdf(data: dict[str, object]) -> list[Requirement]:
    """Extract requirements referenced in PDF spec."""
    reqs: list[Requirement] = []
    raw_reqs = data.get("requirements")
    if not isinstance(raw_reqs, list):
        return reqs

    doc_id = data.get("document_id", "")
    if not isinstance(doc_id, str):
        doc_id = ""

    for r in raw_reqs:
        if not isinstance(r, dict):
            continue
        reqs.append(
            Requirement(
                req_id=str(r.get("id", "")),
                text=str(r.get("text", "")),
                asil=str(r.get("asil", "QM")),
                source_document=doc_id,
            )
        )
    return reqs


def extract_can_signals_from_pdf(data: dict[str, object]) -> list[CANSignal]:
    """Extract CAN signal definitions from PDF spec."""
    signals: list[CANSignal] = []
    raw_signals = data.get("can_signals")
    if not isinstance(raw_signals, list):
        return signals

    doc_id = data.get("document_id", "")
    if not isinstance(doc_id, str):
        doc_id = ""

    for s in raw_signals:
        if not isinstance(s, dict):
            continue
        signals.append(
            CANSignal(
                message_name=str(s.get("message", "")),
                message_id=str(s.get("message_id", "")),
                signal_name=str(s.get("signal", "")),
                start_bit=int(s.get("start_bit", 0)),
                length=int(s.get("length", 0)),
                scale=float(s.get("scale", 1.0)),
                offset=float(s.get("offset", 0)),
                unit=str(s.get("unit", "")),
                document_id=doc_id,
            )
        )
    return signals


def extract_flow_steps(data: dict[str, object]) -> list[FlowStep]:
    """Extract flow diagram steps from PDF spec."""
    steps: list[FlowStep] = []
    flow = data.get("flow_diagram")
    if not isinstance(flow, dict):
        return steps

    raw_steps = flow.get("steps")
    if not isinstance(raw_steps, list):
        return steps

    doc_id = data.get("document_id", "")
    if not isinstance(doc_id, str):
        doc_id = ""

    for s in raw_steps:
        if not isinstance(s, dict):
            continue
        steps.append(
            FlowStep(
                step_id=str(s.get("id", "")),
                label=str(s.get("label", "")),
                step_type=str(s.get("type", "action")),
                next_pass=str(s.get("pass", "")),
                next_fail=str(s.get("fail", "")),
                document_id=doc_id,
            )
        )
    return steps
