"""FastAPI interface"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core.orchestrator import Archon
from core.models import DeploymentPlan
from core.config import config

app = FastAPI(title="Archon 3.0", version="3.0.0")

class GenerateRequest(BaseModel):
    deployment_plan: DeploymentPlan
    project_description: str

@app.get("/")
async def root():
    return {"service": "Archon 3.0", "status": "operational"}

@app.post("/generate")
async def generate_project(request: GenerateRequest):
    if not config.validate():
        raise HTTPException(500, "API keys not configured")
    
    archon = Archon()
    project = archon.generate_project(request.deployment_plan, request.project_description)
    
    return {
        "success": True,
        "project_name": project.project_name,
        "modules": len(project.modules),
        "output_path": f"output/{project.project_name}"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
