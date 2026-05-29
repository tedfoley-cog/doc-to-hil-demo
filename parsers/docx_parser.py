"""Parse Word document extractions (CAN catalogs, DTC matrices)."""

from __future__ import annotations

import json
from pathlib import Path

from parsers.models import (
    CANSignal,
    DiagnosticCode,
    DocumentType,
    ParsedDocument,
)


def parse_can_catalog(extracted_json_path: Path) -> tuple[ParsedDocument, list[CANSignal]]:
    """Parse CAN signal catalog from pre-extracted JSON.

    In production, this would use python-docx to read .docx tables directly.
    The demo uses pre-extracted JSON that represents what the parser produces.
    """
    with open(extracted_json_path) as f:
        data = json.load(f)

    doc = ParsedDocument(
        document_id=data["document_id"],
        title=data["title"],
        doc_type=DocumentType.WORD_SIGNALS,
        source_path=str(extracted_json_path),
        revision=data.get("revision", ""),
    )

    signals: list[CANSignal] = []
    for msg in data.get("messages", []):
        msg_name = msg["name"]
        msg_id = msg["id"]
        for sig in msg.get("signals", []):
            signals.append(
                CANSignal(
                    message_name=msg_name,
                    message_id=msg_id,
                    signal_name=sig["name"],
                    start_bit=sig["start_bit"],
                    length=sig["length"],
                    scale=sig.get("scale", 1.0),
                    offset=sig.get("offset", 0.0),
                    unit=sig.get("unit", ""),
                    min_val=sig.get("min", 0.0),
                    max_val=sig.get("max", 0.0),
                    byte_order=sig.get("byte_order", "little_endian"),
                    document_id=doc.document_id,
                )
            )

    return doc, signals


def parse_dtc_matrix(
    extracted_json_path: Path,
) -> tuple[ParsedDocument, list[DiagnosticCode]]:
    """Parse DTC matrix from pre-extracted JSON."""
    with open(extracted_json_path) as f:
        data = json.load(f)

    doc = ParsedDocument(
        document_id=data["document_id"],
        title=data["title"],
        doc_type=DocumentType.WORD_DTC,
        source_path=str(extracted_json_path),
        revision=data.get("revision", ""),
    )

    dtcs: list[DiagnosticCode] = []
    for d in data.get("dtcs", []):
        dtcs.append(
            DiagnosticCode(
                code=d["code"],
                description=d["description"],
                enable_condition=d["enable_condition"],
                fault_action=d["fault_action"],
                debounce=d["debounce"],
                mil=d.get("mil", False),
                category=d.get("category", "powertrain"),
                document_id=doc.document_id,
            )
        )

    for xref in data.get("cross_references", []):
        code = xref["dtc"]
        for dtc in dtcs:
            if dtc.code == code:
                dtc.related_requirement = xref.get("requirement", "")
                dtc.related_signal = xref.get("signal", "")
                break

    return doc, dtcs
