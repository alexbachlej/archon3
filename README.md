# ARCHON 3.0

[![CI](https://github.com/alexbachlej/archon3/actions/workflows/ci.yml/badge.svg)](https://github.com/alexbachlej/archon3/actions/workflows/ci.yml)

Multi-agent orchestration system for coordinating planning, execution, review, and handoff across LLM-driven software tasks.

---

## What this is

Archon 3.0 is an orchestration runtime for AI-driven software generation.

It coordinates multiple specialized agents in a structured pipeline:

```
Architect → Builder → Validator → Integrator
```

Each phase is a discrete, replaceable agent. The pipeline tracks state across modules, handles retries, and produces a structured project output — not a one-shot generation.

---

## Core Idea

Most AI code tools generate code in a single pass.

Archon structures the build as a supervised execution process:

```
Input → Plan → Build → Validate → Integrate → Output
```

The Validator phase catches module failures and triggers targeted retries before the Integrator assembles the final deliverable. State is persisted in `archon_state.json` so runs are resumable.

---

## Architecture

**Phase 1 — Architect**
Reads a `DeploymentPlan` and a project description. Generates a structured `ArchitectureBlueprint` (modules, dependency order, per-module specs).

**Phase 2 — Builder**
Iterates the blueprint module list. Generates each module file against its spec.

**Phase 3 — Validator**
Checks each generated output against its spec. Records pass/fail. Triggers retry loops for failed modules up to `MAX_RETRIES`.

**Phase 4 — Integrator**
Assembles the validated modules into a complete project structure with `requirements.txt`, `README.md`, and optional Docker config.

---

## Demo

Input files live in `input/`. A minimal run:

```python
from core.orchestrator import Archon

plan = Archon.load_deployment_plan("input/example_plan.json")
description = Archon.load_project_description("input/example_description.md")

archon = Archon()
project = archon.generate_project(plan, description)
```

Example plan (`input/example_plan.json`):

```json
{
  "project_name": "example_api",
  "tech_stack": { "language": "python", "framework": "fastapi" },
  "phases": [{
    "phase_id": 1,
    "name": "Core",
    "modules": [{
      "module_id": "auth",
      "name": "Authentication",
      "dependencies": [],
      "files": ["auth/handlers.py"],
      "description": "JWT authentication"
    }]
  }]
}
```

Output written to `output/` — module files, integration layer, `requirements.txt`, `README.md`, and `archon_state.json`.

---

## Project State

`archon_state.json` records:

- completed modules
- failed modules and retry counts
- per-phase decisions
- full run metadata

Runs are resumable from state.

---

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set OPENAI_API_KEY and ANTHROPIC_API_KEY in .env
```

---

## Output

```
output/
  <module_files>
  requirements.txt
  README.md
  Dockerfile          (optional)
archon_state.json
```

---

## Status

Core pipeline is functional. Designed for architecture experimentation and controlled AI-driven software generation. Not hardened for production deployment.

Archon 3.0 is the architectural base extracted from ForgeBoss — an AI execution runtime for controlled software delivery.

---

## License

MIT
