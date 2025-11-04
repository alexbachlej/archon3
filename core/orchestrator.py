"""Main Orchestrator - Coordinates all 4 phases"""
import json
from pathlib import Path
from core.models import DeploymentPlan, IntegratedProject
from core.architect.architect import Architect
from core.builder.builder import Builder
from core.validator.validator import Validator
from core.integrator.integrator import Integrator
from core.config import config

class Archon:
    def __init__(self):
        self.architect = Architect()
        self.builder = Builder()
        self.validator = Validator()
        self.integrator = Integrator()
    
    def generate_project(self, deployment_plan: DeploymentPlan, project_description: str) -> IntegratedProject:
        print("\n" + "="*60)
        print(f"🚀 ARCHON 3.0 - {deployment_plan.project_name}")
        print("="*60)
        
        # Phase 1: Architecture
        print("\n📐 PHASE 1: ARCHITECTURE")
        blueprint = self.architect.generate_blueprint(deployment_plan, project_description)
        
        # Phase 2 & 3: Build + Validate
        print("\n🔨 PHASE 2 & 3: BUILD + VALIDATE")
        generated_modules = []
        
        for module_id in blueprint.execution_order:
            module_spec = blueprint.module_specs[module_id]
            module = None
            
            for retry in range(config.MAX_RETRIES):
                try:
                    # Build module
                    module = self.builder.build_module(
                        module_id, module_spec, deployment_plan.tech_stack.model_dump()
                    )
                    
                    # Validate module
                    validation = self.validator.validate_module(module, module_spec)
                    module.validation_result = validation
                    
                    if validation.passed:
                        generated_modules.append(module)
                        break
                    elif retry < config.MAX_RETRIES - 1:
                        print(f"⚠️  Validation failed, retry {retry+1}/{config.MAX_RETRIES}")
                        critical = [i.description for i in validation.issues if i.severity == 'critical']
                        print(f"   Issues: {critical[:2]}")  # Show first 2 issues
                    else:
                        print(f"⚠️  Module '{module_id}' has issues but continuing...")
                        generated_modules.append(module)
                
                except Exception as e:
                    if retry < config.MAX_RETRIES - 1:
                        print(f"⚠️  Error in module '{module_id}', retry {retry+1}/{config.MAX_RETRIES}")
                        print(f"   Error: {str(e)[:100]}")
                    else:
                        print(f"❌ Module '{module_id}' failed after {config.MAX_RETRIES} attempts")
                        # Create empty module as placeholder
                        from core.models import GeneratedModule, ValidationResult
                        module = GeneratedModule(
                            module_id=module_id,
                            files={f"{module_id}/placeholder.py": "# Failed to generate"},
                            validation_result=ValidationResult(module_id=module_id, passed=False, issues=[])
                        )
                        generated_modules.append(module)
                        break
        
        # Phase 4: Integration
        print("\n🔗 PHASE 4: INTEGRATION")
        integrated = self.integrator.integrate_project(
            deployment_plan.project_name,
            generated_modules,
            blueprint.model_dump(),
            deployment_plan.deployment.model_dump()
        )
        
        # Save output
        output_path = Path(config.OUTPUT_DIR) / deployment_plan.project_name
        self._save_project(integrated, output_path)
        
        print("\n" + "="*60)
        print(f"✅ COMPLETE: {output_path.absolute()}")
        print("="*60 + "\n")
        
        return integrated
    
    def _save_project(self, project: IntegratedProject, output_path: Path):
        output_path.mkdir(parents=True, exist_ok=True)
        
        for module in project.modules:
            for filepath, content in module.files.items():
                file_path = output_path / filepath
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
        
        for filepath, content in project.integration_files.items():
            file_path = output_path / filepath
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
        
        (output_path / "requirements.txt").write_text(project.requirements_txt)
        (output_path / "README.md").write_text(project.readme)
        
        for filename, content in project.docker_files.items():
            (output_path / filename).write_text(content)
    
    @staticmethod
    def load_deployment_plan(filepath: str) -> DeploymentPlan:
        with open(filepath) as f:
            return DeploymentPlan(**json.load(f))
    
    @staticmethod
    def load_project_description(filepath: str) -> str:
        with open(filepath) as f:
            return f.read()
