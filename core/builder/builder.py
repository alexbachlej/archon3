"""Claude Builder - Phase 2 - FILE BY FILE"""
import json
from anthropic import Anthropic
from core.models import GeneratedModule
from core.config import config

class Builder:
    def __init__(self):
        self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.model = config.CLAUDE_MODEL
    
    def build_module(self, module_id: str, module_spec: dict, tech_stack: dict) -> GeneratedModule:
        print(f"🔨 Building '{module_id}'...")
        
        files = {}
        
        # Get file list from module_spec (from architect) or use default
        file_list = module_spec.get('files', [])
        if not file_list:
            # Fallback: create default file structure
            file_list = [f"{module_id}/main.py", f"{module_id}/__init__.py"]
            print(f"   ⚠️  No files specified, using defaults: {file_list}")
        
        # Generate each file separately
        for filepath in file_list:
            print(f"   Generating {filepath}...")
            code = self._generate_single_file(module_id, filepath, module_spec, tech_stack)
            files[filepath] = code
        
        module = GeneratedModule(module_id=module_id, files=files)
        print(f"✅ '{module_id}': {len(module.files)} files")
        return module
    
    def _generate_single_file(self, module_id: str, filepath: str, module_spec: dict, tech_stack: dict) -> str:
        """Generate a single file"""
        
        prompt = f"""Generate production-ready code for this file.

Module: {module_id}
File: {filepath}
Purpose: {module_spec.get('description', 'N/A')}
Technical details: {module_spec.get('technical_details', 'Standard implementation')}
Tech stack: {tech_stack.get('language', 'python')} + {tech_stack.get('framework', 'standard library')}

Requirements:
- Type hints on all functions
- Comprehensive docstrings (Google style)
- Proper error handling (try/except where needed)
- Use environment variables for secrets (never hardcode)
- Security best practices (password hashing, JWT validation, rate limiting)
- Production-ready, clean code

Output ONLY the Python code. No explanations, no markdown, no ```python blocks.
Start directly with imports or code."""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            temperature=config.TEMPERATURE_BUILDER,
            messages=[{"role": "user", "content": prompt}]
        )
        
        code = response.content[0].text
        
        # Remove markdown code blocks if present
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0]
        elif "```" in code:
            code = code.split("```")[1].split("```")[0]
        
        return code.strip()
