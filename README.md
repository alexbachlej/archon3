# 🚀 ARCHON 3.0

AI Code Generator with Integration Orchestration

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

## Usage
```python
from core.orchestrator import Archon
from core.models import DeploymentPlan

plan = Archon.load_deployment_plan("input/deployment_plan.json")
description = Archon.load_project_description("input/description.md")

archon = Archon()
project = archon.generate_project(plan, description)
```

## Architecture
- Phase 1: GPT-5 Architect
- Phase 2: Claude Builder  
- Phase 3: GPT-5 Validator
- Phase 4: GPT-5 Integrator (CORE FEATURE)

Built to crush competition with dual-AI orchestration 🔥
