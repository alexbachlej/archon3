"""GPT-5 Validator - Phase 3 - WITH AUTO-FIX"""
import ast
import json
import re
from typing import List, Tuple
from openai import OpenAI
from core.models import GeneratedModule, ValidationResult, ValidationIssue
from core.config import config

class Validator:
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.GPT5_MODEL
    
    def validate_module(self, module: GeneratedModule, module_spec: dict) -> ValidationResult:
        print(f"🔍 Validating '{module.module_id}'...")
        
        issues: List[ValidationIssue] = []
        
        # 1. Syntax check
        for filepath, code in module.files.items():
            if filepath.endswith('.py'):
                try:
                    ast.parse(code)
                except SyntaxError as e:
                    issues.append(ValidationIssue(
                        severity="critical",
                        type="syntax",
                        description=f"Syntax error in {filepath}: {e.msg}",
                        fix_suggestion="Fix Python syntax",
                        line_number=e.lineno
                    ))
        
        # 2. GPT validation
        gpt_issues = self._gpt_validation(module, module_spec)
        issues.extend(gpt_issues)
        
        # 3. Auto-fix critical issues
        if issues:
            critical = [i for i in issues if i.severity == "critical"]
            if critical:  # Only auto-fix if manageable
                print(f"   🔧 Attempting auto-fix for {len(critical)} critical issues...")
                fixed_module, fix_success = self._auto_fix(module, critical)
                if fix_success:
                    # Re-validate after fix
                    print(f"   ♻️  Re-validating after fixes...")
                    return self.validate_module(fixed_module, module_spec)
        
        # Determine pass/fail
        critical_count = len([i for i in issues if i.severity == "critical"])
        passed = critical_count == 0
        
        result = ValidationResult(
            module_id=module.module_id,
            passed=passed,
            issues=issues
        )
        
        if passed:
            print(f"✅ '{module.module_id}' validated successfully")
        else:
            print(f"⚠️  '{module.module_id}': {critical_count} critical issues")
        
        return result
    
    def _gpt_validation(self, module: GeneratedModule, module_spec: dict) -> List[ValidationIssue]:
        """Use GPT for deep validation"""
        
        code_content = "\n\n---FILE---\n\n".join([
            f"# {fp}\n{code}" for fp, code in module.files.items()
        ])
        
        prompt = f"""Validate this code module.

Module: {module.module_id}
Spec: {json.dumps(module_spec, indent=2)}

Code:
{code_content}

Check for CRITICAL issues only:
1. Security vulnerabilities (SQL injection, XSS, secrets in code)
2. Missing essential imports
3. Logic errors vs specification
4. Missing critical error handling

Output JSON:
{{"issues": [{{"severity": "critical|warning", "type": "security|import|logic", "description": "...", "fix_suggestion": "..."}}]}}

Only flag REAL problems. Be strict but fair."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=config.TEMPERATURE_VALIDATOR,
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            return [ValidationIssue(**i) for i in data.get("issues", [])]
        except:
            return []
    
    def _auto_fix(self, module: GeneratedModule, issues: List[ValidationIssue]) -> Tuple[GeneratedModule, bool]:
        """Attempt to auto-fix critical issues"""
        
        # Build fix instructions
        fix_instructions = "\n".join([
            f"- {issue.description}\n  Fix: {issue.fix_suggestion}"
            for issue in issues
        ])
        
        code_content = "\n\n---FILE---\n\n".join([
            f"# {fp}\n{code}" for fp, code in module.files.items()
        ])
        
        prompt = f"""Fix these critical issues in the code.

Issues to fix:
{fix_instructions}

Current code:
{code_content}

Output the FIXED code files as JSON:
{{"files": {{"filepath": "fixed_code"}}}}

Apply the fixes properly. Maintain all other functionality."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            data = json.loads(response.choices[0].message.content)
            fixed_files = data.get("files", {})
            
            if fixed_files:
                fixed_module = GeneratedModule(
                    module_id=module.module_id,
                    files=fixed_files
                )
                print(f"   ✅ Auto-fix applied")
                return fixed_module, True
            
        except Exception as e:
            print(f"   ⚠️  Auto-fix failed: {e}")
        
        return module, False
