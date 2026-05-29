"""Tests for document parsers."""

from __future__ import annotations

import json
from pathlib import Path

from parsers.docx_parser import parse_can_catalog, parse_dtc_matrix
from parsers.excel_parser import parse_requirements_xlsx, parse_test_parameters_xlsx
from parsers.models import DocumentType
from parsers.pdf_parser import (
    extract_can_signals_from_pdf,
    extract_flow_steps,
    extract_requirements_from_pdf,
    extract_states,
    extract_transitions,
    parse_pdf_spec,
)


def test_parse_power_modes_pdf(source_dir: Path) -> None:
    json_path = source_dir / "pdf_specs" / "pcm_power_modes.extracted.json"
    doc = parse_pdf_spec(json_path)
    assert doc.document_id == "PCM-SPEC-2024-001"
    assert doc.doc_type == DocumentType.PDF_SPEC


def test_extract_states(source_dir: Path) -> None:
    json_path = source_dir / "pdf_specs" / "pcm_power_modes.extracted.json"
    with open(json_path) as f:
        data = json.load(f)
    states = extract_states(data)
    assert len(states) == 6
    state_ids = {s.state_id for s in states}
    assert "OFF" in state_ids
    assert "EMERGENCY_STOP" in state_ids


def test_extract_transitions(source_dir: Path) -> None:
    json_path = source_dir / "pdf_specs" / "pcm_power_modes.extracted.json"
    with open(json_path) as f:
        data = json.load(f)
    transitions = extract_transitions(data)
    assert len(transitions) == 11
    assert any(t.from_state == "OFF" and t.to_state == "ACC" for t in transitions)


def test_extract_requirements_from_pdf(source_dir: Path) -> None:
    json_path = source_dir / "pdf_specs" / "pcm_power_modes.extracted.json"
    with open(json_path) as f:
        data = json.load(f)
    reqs = extract_requirements_from_pdf(data)
    assert len(reqs) == 5
    assert reqs[0].req_id == "REQ-PM-001"


def test_extract_can_signals(source_dir: Path) -> None:
    json_path = source_dir / "pdf_specs" / "pcm_power_modes.extracted.json"
    with open(json_path) as f:
        data = json.load(f)
    signals = extract_can_signals_from_pdf(data)
    assert len(signals) == 9
    assert signals[0].message_name == "PCM_Status_1"


def test_extract_flow_steps(source_dir: Path) -> None:
    json_path = source_dir / "pdf_specs" / "transmission_shift_logic.extracted.json"
    with open(json_path) as f:
        data = json.load(f)
    steps = extract_flow_steps(data)
    assert len(steps) == 11
    assert steps[0].step_id == "SHIFT_REQ"


def test_extract_shift_transitions(source_dir: Path) -> None:
    json_path = source_dir / "pdf_specs" / "transmission_shift_logic.extracted.json"
    with open(json_path) as f:
        data = json.load(f)
    transitions = extract_transitions(data)
    assert len(transitions) == 6


def test_parse_requirements_xlsx(source_dir: Path) -> None:
    xlsx_path = source_dir / "excel" / "system_requirements.xlsx"
    if not xlsx_path.exists():
        return
    doc, reqs = parse_requirements_xlsx(xlsx_path)
    assert doc.doc_type == DocumentType.EXCEL_REQ
    assert len(reqs) >= 10


def test_parse_test_parameters_xlsx(source_dir: Path) -> None:
    xlsx_path = source_dir / "excel" / "test_parameters.xlsx"
    if not xlsx_path.exists():
        return
    doc, params = parse_test_parameters_xlsx(xlsx_path)
    assert doc.doc_type == DocumentType.EXCEL_PARAMS
    assert len(params) >= 8


def test_parse_can_catalog(source_dir: Path) -> None:
    json_path = source_dir / "word_docs" / "can_signal_catalog.extracted.json"
    doc, signals = parse_can_catalog(json_path)
    assert doc.document_id == "CAN-CAT-2024-001"
    assert len(signals) >= 20


def test_parse_dtc_matrix(source_dir: Path) -> None:
    json_path = source_dir / "word_docs" / "diagnostic_dtc_matrix.extracted.json"
    doc, dtcs = parse_dtc_matrix(json_path)
    assert doc.document_id == "DIAG-SPEC-2024-002"
    assert len(dtcs) == 20
    p0730 = next(d for d in dtcs if d.code == "P0730")
    assert p0730.related_requirement == "REQ-TR-009"
