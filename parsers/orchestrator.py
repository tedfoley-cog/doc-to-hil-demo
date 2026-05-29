"""Orchestrate parsing of all source documents into a unified inventory."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from parsers.docx_parser import parse_can_catalog, parse_dtc_matrix
from parsers.excel_parser import parse_requirements_xlsx, parse_test_parameters_xlsx
from parsers.models import DocumentInventory, EntityRelationship, EntityType, ParsedEntity
from parsers.pdf_parser import (
    extract_can_signals_from_pdf,
    extract_flow_steps,
    extract_requirements_from_pdf,
    extract_states,
    extract_transitions,
    parse_pdf_spec,
)


def run_all_parsers(source_dir: Path) -> DocumentInventory:
    """Parse all source documents and build a unified inventory."""
    inventory = DocumentInventory()

    pdf_dir = source_dir / "pdf_specs"
    for json_file in sorted(pdf_dir.glob("*.extracted.json")):
        with open(json_file) as f:
            data = json.load(f)

        doc = parse_pdf_spec(json_file)
        states = extract_states(data)
        transitions = extract_transitions(data)
        requirements = extract_requirements_from_pdf(data)
        signals = extract_can_signals_from_pdf(data)
        flow_steps = extract_flow_steps(data)

        for s in states:
            doc.entities.append(
                ParsedEntity(
                    entity_id=s.state_id,
                    entity_type=EntityType.STATE,
                    label=s.name,
                    properties={"code": s.code, "description": s.description},
                    source_document=doc.document_id,
                )
            )

        for t in transitions:
            doc.entities.append(
                ParsedEntity(
                    entity_id=f"{t.from_state}->{t.to_state}",
                    entity_type=EntityType.TRANSITION,
                    label=f"{t.from_state} -> {t.to_state}",
                    properties={
                        "condition": t.condition,
                        "guard": t.guard,
                        "timeout_ms": t.timeout_ms,
                    },
                    source_document=doc.document_id,
                )
            )

        for r in requirements:
            doc.entities.append(
                ParsedEntity(
                    entity_id=r.req_id,
                    entity_type=EntityType.REQUIREMENT,
                    label=r.text,
                    properties={"asil": r.asil},
                    source_document=doc.document_id,
                )
            )

        for sig in signals:
            doc.entities.append(
                ParsedEntity(
                    entity_id=f"{sig.message_name}.{sig.signal_name}",
                    entity_type=EntityType.SIGNAL,
                    label=sig.signal_name,
                    properties={
                        "message": sig.message_name,
                        "message_id": sig.message_id,
                        "start_bit": sig.start_bit,
                        "length": sig.length,
                        "scale": sig.scale,
                        "unit": sig.unit,
                    },
                    source_document=doc.document_id,
                )
            )

        for step in flow_steps:
            doc.entities.append(
                ParsedEntity(
                    entity_id=step.step_id,
                    entity_type=EntityType.FLOW_STEP,
                    label=step.label,
                    properties={"type": step.step_type},
                    source_document=doc.document_id,
                )
            )

        inventory.total_states += len(states)
        inventory.total_transitions += len(transitions)
        inventory.total_requirements += len(requirements)
        inventory.total_signals += len(signals)
        inventory.total_flow_steps += len(flow_steps)
        inventory.documents.append(doc)

    excel_dir = source_dir / "excel"
    for xlsx_file in sorted(excel_dir.glob("*.xlsx")):
        if "requirements" in xlsx_file.stem.lower():
            doc, reqs = parse_requirements_xlsx(xlsx_file)
            for r in reqs:
                doc.entities.append(
                    ParsedEntity(
                        entity_id=r.req_id,
                        entity_type=EntityType.REQUIREMENT,
                        label=r.text,
                        properties={
                            "asil": r.asil,
                            "verification": r.verification_method,
                        },
                        source_document=doc.document_id,
                    )
                )
            inventory.total_requirements += len(reqs)
            inventory.documents.append(doc)
        elif "parameters" in xlsx_file.stem.lower():
            doc, params = parse_test_parameters_xlsx(xlsx_file)
            inventory.documents.append(doc)

    word_dir = source_dir / "word_docs"
    can_json = word_dir / "can_signal_catalog.extracted.json"
    if can_json.exists():
        doc, signals = parse_can_catalog(can_json)
        for sig in signals:
            doc.entities.append(
                ParsedEntity(
                    entity_id=f"{sig.message_name}.{sig.signal_name}",
                    entity_type=EntityType.SIGNAL,
                    label=sig.signal_name,
                    properties={
                        "message": sig.message_name,
                        "message_id": sig.message_id,
                        "start_bit": sig.start_bit,
                        "length": sig.length,
                        "scale": sig.scale,
                        "unit": sig.unit,
                    },
                    source_document=doc.document_id,
                )
            )
        inventory.total_signals += len(signals)
        inventory.documents.append(doc)

    dtc_json = word_dir / "diagnostic_dtc_matrix.extracted.json"
    if dtc_json.exists():
        doc, dtcs = parse_dtc_matrix(dtc_json)
        for d in dtcs:
            rels: list[EntityRelationship] = []
            if d.related_requirement:
                rels.append(
                    EntityRelationship(
                        source_id=d.code,
                        target_id=d.related_requirement,
                        relationship_type="related_requirement",
                    )
                )
            if d.related_signal:
                rels.append(
                    EntityRelationship(
                        source_id=d.code,
                        target_id=d.related_signal,
                        relationship_type="related_signal",
                    )
                )
            doc.entities.append(
                ParsedEntity(
                    entity_id=d.code,
                    entity_type=EntityType.DTC,
                    label=d.description,
                    properties={
                        "enable_condition": d.enable_condition,
                        "fault_action": d.fault_action,
                        "mil": d.mil,
                        "category": d.category,
                    },
                    source_document=doc.document_id,
                    relationships=rels,
                )
            )
        inventory.total_dtcs += len(dtcs)
        inventory.documents.append(doc)

    return inventory


def main() -> None:
    """CLI entrypoint: parse all documents and write inventory JSON."""
    source_dir = Path("source_documents")
    if len(sys.argv) > 1:
        source_dir = Path(sys.argv[1])

    inventory = run_all_parsers(source_dir)

    doc_list: list[dict[str, object]] = []
    for doc in inventory.documents:
        doc_list.append(
            {
                "document_id": doc.document_id,
                "title": doc.title,
                "type": doc.doc_type.value,
                "source_path": doc.source_path,
                "entity_count": len(doc.entities),
                "entities_by_type": _count_by_type(doc.entities),
            }
        )

    output: dict[str, object] = {
        "summary": inventory.summary(),
        "documents": doc_list,
    }

    out_path = Path("dashboard") / "inventory.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Parsed {len(inventory.documents)} documents")
    for key, val in inventory.summary().items():
        print(f"  {key}: {val}")
    print(f"Inventory written to {out_path}")


def _count_by_type(entities: list[ParsedEntity]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for e in entities:
        key = e.entity_type.value
        counts[key] = counts.get(key, 0) + 1
    return counts


if __name__ == "__main__":
    main()
