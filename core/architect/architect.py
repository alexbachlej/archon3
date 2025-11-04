"""GPT-5 Architect - Phase 1"""
import json
from openai import OpenAI
from core.models import DeploymentPlan, ArchitectureBlueprint
from core.config import config

class Architect:
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.GPT5_MODEL
    
    def generate_blueprint(self, deployment_plan: DeploymentPlan, project_description: str) -> ArchitectureBlueprint:
        print(f"🏗️  Architect: Analyzing '{deployment_plan.project_name}'...")
        
        prompt = f"""Generate architecture blueprint.
Project: {deployment_plan.project_name}
Description: {project_description}
Plan: {json.dumps(deployment_plan.model_dump(), indent=2)}

Output JSON with:
- execution_order: [module_ids]
- module_specs: {{module_id: {{inputs, outputs, api_endpoints, dependencies, validation_criteria, technical_details}}}}
- integration_plan: {{shared_imports, api_contracts, error_propagation}}
- dependency_graph: {{module_id: [depends_on]}}
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=config.TEMPERATURE_ARCHITECT,
            response_format={"type": "json_object"}
        )
        
        data = json.loads(response.choices[0].message.content)
        blueprint = ArchitectureBlueprint(
            project_name=deployment_plan.project_name,
            execution_order=data["execution_order"],
            module_specs=data["module_specs"],
            integration_plan=data["integration_plan"],
            dependency_graph=data["dependency_graph"]
        )
        
        print(f"✅ Blueprint: {len(blueprint.execution_order)} modules")
        return blueprint
