"""Data models for parsed document entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DocumentType(Enum):
    PDF_SPEC = "pdf_spec"
    EXCEL_REQ = "excel_requirement"
    EXCEL_PARAMS = "excel_parameters"
    WORD_SIGNALS = "word_signals"
    WORD_DTC = "word_dtc"


class EntityType(Enum):
    STATE = "state"
    TRANSITION = "transition"
    SIGNAL = "signal"
    REQUIREMENT = "requirement"
    DTC = "dtc"
    FLOW_STEP = "flow_step"
    SHIFT_SCHEDULE = "shift_schedule"


@dataclass
class ParsedDocument:
    """A parsed source document with extracted entities."""

    document_id: str
    title: str
    doc_type: DocumentType
    source_path: str
    revision: str = ""
    subsystem: str = ""
    asil: str = "QM"
    entities: list[ParsedEntity] = field(default_factory=list)


@dataclass
class ParsedEntity:
    """A single entity extracted from a document."""

    entity_id: str
    entity_type: EntityType
    label: str
    properties: dict[str, Any] = field(default_factory=dict)
    source_document: str = ""
    relationships: list[EntityRelationship] = field(default_factory=list)


@dataclass
class EntityRelationship:
    """A relationship between two entities."""

    source_id: str
    target_id: str
    relationship_type: str
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class State:
    """A state in a state machine extracted from a spec."""

    state_id: str
    name: str
    code: str = ""
    description: str = ""
    document_id: str = ""


@dataclass
class Transition:
    """A transition between states."""

    from_state: str
    to_state: str
    condition: str
    guard: str = ""
    timeout_ms: int | None = None
    document_id: str = ""


@dataclass
class CANSignal:
    """A CAN bus signal definition."""

    message_name: str
    message_id: str
    signal_name: str
    start_bit: int
    length: int
    scale: float = 1.0
    offset: float = 0.0
    unit: str = ""
    min_val: float = 0.0
    max_val: float = 0.0
    byte_order: str = "little_endian"
    document_id: str = ""


@dataclass
class Requirement:
    """A system requirement extracted from a document."""

    req_id: str
    text: str
    asil: str = "QM"
    verification_method: str = "test"
    source_document: str = ""
    related_signals: list[str] = field(default_factory=list)
    related_dtcs: list[str] = field(default_factory=list)


@dataclass
class DiagnosticCode:
    """A diagnostic trouble code (DTC)."""

    code: str
    description: str
    enable_condition: str
    fault_action: str
    debounce: str
    mil: bool = False
    category: str = "powertrain"
    related_requirement: str = ""
    related_signal: str = ""
    document_id: str = ""


@dataclass
class FlowStep:
    """A step in a flow diagram."""

    step_id: str
    label: str
    step_type: str  # start, action, decision, end, terminal
    next_pass: str = ""
    next_fail: str = ""
    document_id: str = ""


@dataclass
class DocumentInventory:
    """Complete inventory of all parsed documents and entities."""

    documents: list[ParsedDocument] = field(default_factory=list)
    total_states: int = 0
    total_transitions: int = 0
    total_signals: int = 0
    total_requirements: int = 0
    total_dtcs: int = 0
    total_flow_steps: int = 0

    def summary(self) -> dict[str, int]:
        """Return entity count summary."""
        return {
            "documents": len(self.documents),
            "states": self.total_states,
            "transitions": self.total_transitions,
            "signals": self.total_signals,
            "requirements": self.total_requirements,
            "dtcs": self.total_dtcs,
            "flow_steps": self.total_flow_steps,
        }
