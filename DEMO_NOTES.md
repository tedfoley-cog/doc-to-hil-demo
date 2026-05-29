# Demo Cheat Sheet — Document-to-HIL Pipeline

## Setup (do this before joining the call)
- [ ] Open the repo in a browser tab: https://github.com/tedfoley-cog/doc-to-hil-demo
- [ ] Have a Devin session ready to trigger against the repo
- [ ] Pre-open `localhost:5001` in a browser tab (dashboard will populate during demo)

## Demo Flow
1. Walk through `source_documents/` — show the variety: PDF specs with state machines and tables, Excel requirements, Word signal catalogs. Point out that these are realistic OEM document formats that engineers currently Ctrl+F through manually.
2. Trigger Devin to run the full pipeline. Devin parses all documents, builds the knowledge graph, generates test scripts, and executes them against the SIL harness. Narrate each stage as the dashboard updates in real time.
3. Switch to the dashboard tab — show the document inventory (how many entities were extracted from each source), knowledge graph metrics (nodes/edges by type), and SIL test results with pass/fail verdicts linked to requirements.
4. Show the generated test scripts in `hil_output/generated/` — each one traces back to a specific state machine transition and requirement. This is the traceability the customer asked about.
5. Devin opens a PR with all artifacts. Point out that what took a week of manual analysis was completed in minutes, and every test is traceable back to source documents.
