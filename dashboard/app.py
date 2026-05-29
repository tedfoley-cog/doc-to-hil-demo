"""FastAPI dashboard for document comprehension and test results."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Document-to-HIL Dashboard")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

DASHBOARD_DIR = Path(__file__).parent


def _load_json(filename: str) -> dict[str, object]:
    path = DASHBOARD_DIR / filename
    if path.exists():
        with open(path) as f:
            return json.load(f)  # type: ignore[no-any-return]
    return {}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """Main dashboard page."""
    state = _load_json("state.json")
    inventory = _load_json("inventory.json")
    knowledge_graph = _load_json("knowledge_graph.json")
    test_manifest = _load_json("test_manifest.json")
    test_results = _load_json("test_results.json")

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "state": state,
            "inventory": inventory,
            "knowledge_graph": knowledge_graph,
            "test_manifest": test_manifest,
            "test_results": test_results,
        },
    )


@app.get("/api/state")
async def get_state() -> dict[str, object]:
    """Return current pipeline state."""
    return _load_json("state.json")


@app.get("/api/inventory")
async def get_inventory() -> dict[str, object]:
    """Return document inventory."""
    return _load_json("inventory.json")


@app.get("/api/knowledge-graph")
async def get_knowledge_graph() -> dict[str, object]:
    """Return knowledge graph data."""
    return _load_json("knowledge_graph.json")


@app.get("/api/test-results")
async def get_test_results() -> dict[str, object]:
    """Return SIL test results."""
    return _load_json("test_results.json")
