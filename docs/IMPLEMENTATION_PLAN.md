# Implementation Plan — Document-to-HIL Demo

> Committed before the rest of the scaffold per the Demo Scaffold playbook (Step 2b).

## 1. What the demo proves

Devin can ingest **unstructured automotive engineering documents** — PDF
specifications containing state machine diagrams, flow charts, and complex
tables; Excel workbooks with requirements matrices and test parameters; Word
documents with CAN signal catalogs and diagnostic procedures — parse them into a
**structured knowledge graph**, and then use that graph to **generate and execute
HIL/SIL test cases** automatically. A root-cause analysis workflow that currently
takes an engineer ~1 week of manual Ctrl+F searching is reduced to ~15 minutes.

## 2. What Devin does live (one sentence)

Parse varied unstructured spec documents (PDFs, Excel, Word) into a structured
knowledge graph, generate HIL/SIL test scripts from the extracted state machines
and signal definitions, execute them against a SIL replay harness, and produce a
traceability dashboard linking every test back to its source document.

## 3. Stack and rationale

| Layer | Choice | Why | Source |
|---|---|---|---|
| Domain | Powertrain Control Module (PCM) — power modes + transmission | Rich in state machines, shift tables, and flow diagrams; familiar to OEM audiences; natural fit for HIL/SIL testing | SAE J1979 diagnostic standards; ISO 15031 |
| Document formats | PDF (state machines, tables), Excel (requirements), Word (CAN signals, DTCs) | Covers the three main unstructured formats described in the customer's current workflow | Customer discovery call notes |
| Spec representation | Markdown source + pre-extracted JSON | Real PDF/Word parsing requires proprietary tools (Adobe SDK, python-docx); demo uses pre-extracted JSON with markdown originals to show what the parser produces. Live demo could wire in real PDF parsing via PyMuPDF/Camelot | PyMuPDF docs; Camelot docs |
| Excel parsing | openpyxl | Standard Python library for reading .xlsx files; already used in l3-hil-verification-demo | openpyxl.readthedocs.io |
| Knowledge graph | In-memory Python graph with typed nodes and edges | Lightweight dependency graph connecting requirements → signals → states → transitions → DTCs; queryable for impact analysis | NetworkX-style pattern |
| Test generation | Jinja2 templates → Python test scripts | Same pattern as ecu-bms-controller and l3-hil-verification-demo; generates ASAM XIL-style test procedures | ASAM XIL 3.0 Framework spec |
| SIL harness | Python replay of pre-captured JSON traces | Real HIL hardware unreachable from Devin VM; replay produces identical signal DataFrames for downstream analysis | Same pattern as l3-hil-verification-demo |
| Dashboard | FastAPI + Jinja2, port 5001 | Shows document inventory, extracted entities, knowledge graph, and test results in a single view | FastAPI docs |
| CI | GitHub Actions: install uv, sync, lint, typecheck, test | Same shape as other tedfoley-cog demo repos | GitHub Actions docs |

## 4. Repo layout

```
README.md
DEMO_NOTES.md
.gitignore
.github/workflows/ci.yml
pyproject.toml

docs/
  IMPLEMENTATION_PLAN.md          # This file
  flowchart.html                  # Demo flow (Mermaid, standalone)
  flowchart.png                   # Rendered PNG for README

source_documents/
  pdf_specs/
    pcm_power_modes.md            # Spec content: power mode state machine + tables
    pcm_power_modes.extracted.json
    transmission_shift_logic.md   # Spec content: shift flow diagram + shift schedule
    transmission_shift_logic.extracted.json
  excel/
    system_requirements.xlsx      # Requirements matrix (openpyxl-readable)
    test_parameters.xlsx          # Test conditions and expected values
  word_docs/
    can_signal_catalog.md         # CAN message/signal definitions
    can_signal_catalog.extracted.json
    diagnostic_dtc_matrix.md      # DTC codes, enable conditions, fault actions
    diagnostic_dtc_matrix.extracted.json

parsers/
  __init__.py
  models.py                      # Data models (Document, State, Transition, Signal, etc.)
  pdf_parser.py                  # Parse PDF spec content → structured entities
  excel_parser.py                # Parse Excel requirements and test parameters
  docx_parser.py                 # Parse Word CAN/DTC content
  orchestrator.py                # Run all parsers, build unified document inventory

comprehension/
  __init__.py
  knowledge_graph.py             # Build dependency graph from parsed entities
  query.py                       # Query graph for impact analysis and traceability

generators/
  __init__.py
  test_generator.py              # Generate HIL/SIL test scripts from knowledge graph
  templates/
    hil_test_template.py.j2      # Jinja2 template for test scripts

sil_harness/
  __init__.py
  executor.py                    # SIL replay harness (mock bench)
  traces/
    power_mode_trace.json        # Pre-captured trace: power mode transitions
    shift_logic_trace.json       # Pre-captured trace: transmission shift sequence

dashboard/
  app.py                         # FastAPI dashboard
  state.json                     # Pipeline state
  templates/
    index.html                   # Document inventory + knowledge graph + test results

hil_output/
  generated/
    .gitkeep                     # Devin fills this live

tests/
  conftest.py
  test_parsers.py
  test_comprehension.py
  test_generator.py
```

~25 source files. Initial state only — `hil_output/generated/` is empty;
Devin fills it during the live demo.

## 5. Flowchart outline

1. **Document Sources** (PDF Specs / Excel Requirements / Word Design Docs)
2. **Devin Session Triggered** (prompt)
3. **Parse Documents** — extract state machines, tables, flow diagrams, signals
4. **Build Knowledge Graph** — connect requirements ↔ signals ↔ states ↔ DTCs
5. **Query for Test Coverage** — identify untested paths, missing coverage
6. **Generate HIL/SIL Tests** — produce test scripts from knowledge graph
7. **Execute SIL Tests** — run against replay harness
8. **Produce Dashboard** — document inventory + graph + test results
9. **Open PR** — all generated artifacts reviewable
10. **Engineer Reviews** — approve or iterate

## 6. Runtime plan

"Appears runnable" via pre-extracted JSON and SIL replay harness. Real PDF
parsing (PyMuPDF/Camelot) and HIL hardware are unreachable from a Devin VM.
The parser reads pre-extracted JSON representations of the source documents;
the SIL harness replays pre-captured traces. Downstream analysis is identical.

Commands:
- `uv sync` — install all dependencies
- `uv run python -m parsers.orchestrator` — parse all source documents
- `uv run python -m comprehension.knowledge_graph` — build knowledge graph
- `uv run python -m generators.test_generator` — generate test scripts
- `uv run python -m sil_harness.executor` — execute SIL tests
- `uv run uvicorn dashboard.app:app --port 5001` — launch dashboard
- `uv run pytest -q` — run unit tests

## 7. CI plan

Single workflow: checkout → install uv → `uv sync` → `uv run ruff check .` →
`uv run mypy parsers/ comprehension/ generators/ tests/` → `uv run pytest -q`.
Under 40 lines of YAML.

## 8. Risks and unknowns

- **PDF parsing fidelity**: Real automotive PDFs contain embedded vector diagrams
  (state machines drawn in Visio/PowerPoint) that require OCR or vector extraction.
  The demo uses pre-extracted JSON; real integration would use PyMuPDF + Camelot
  for tables and a vision model for diagrams.
- **State machine extraction from figures**: Extracting state machines from raster
  images is a vision/ML task. The demo assumes pre-extracted structured data;
  a production system would use a vision model or require diagrams in a
  machine-readable format (e.g., XMI/UML export).
- **CAN DBC format**: Real OEMs use .dbc files (Vector CANdb++) for signal
  definitions. The demo uses a simplified YAML/JSON representation. If the
  customer has .dbc files, those could be wired in directly.
- **Integration APIs**: Jira, Jama, JFrog, SharePoint integrations are mentioned
  as longer-term goals. The demo focuses on the document parsing → test generation
  pipeline; API integrations would be added as follow-up demos.
