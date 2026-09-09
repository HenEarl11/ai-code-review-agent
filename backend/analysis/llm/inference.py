import requests
import json
from typing import List, Dict
import os

class LLMService:
    """Interface with local LLM (Ollama/Ministack)"""
    
    def __init__(self):
        self.ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.model = os.getenv('OLLAMA_MODEL', 'mistral')
    
    def check_health(self) -> dict:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            return {'status': 'healthy', 'available_models': response.json().get('models', [])}
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}
    
    def analyze(self, code: str, file_path: str, parsed_data: dict) -> List[Dict]:
        """
        Use LLM to analyze code for issues
        
        Args:
            code (str): Code to analyze
            file_path (str): Path to file
            parsed_data (dict): Parsed code structure
        
        Returns:
            list: List of detected issues
        """
        issues = []
        
        try:
            # Prepare prompt
            prompt = self._build_prompt(code, file_path, parsed_data)
            
            # Call Ollama
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.3
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                # Parse LLM response
                issues = self._parse_llm_response(result.get('response', ''), file_path)
        
        except requests.exceptions.Timeout:
            # LLM analysis timeout - continue without it
            pass
        except Exception as e:
            # Log error but don't fail analysis
            print(f"LLM analysis error: {e}")
        
        return issues
    
    def _build_prompt(self, code: str, file_path: str, parsed_data: dict) -> str:
        """
        Build prompt for LLM analysis
        """
        return f"""Analyze this code for potential issues (security, performance, bugs, best practices).
Return ONLY a JSON array with objects containing: line, severity (critical/high/medium/low), type, message, suggestion.

File: {file_path}
Code:
```
{code[:2000]}  # Limit to first 2000 chars for context
```

JSON Array:"""
    
    def _parse_llm_response(self, response: str, file_path: str) -> List[Dict]:
        """
        Parse LLM JSON response into issue objects
        """
        issues = []
        
        try:
            # Extract JSON from response
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                parsed_issues = json.loads(json_str)
                
                for issue in parsed_issues:
                    issues.append({
                        'type': 'llm_analysis',
                        'subtype': issue.get('type', 'unknown'),
                        'severity': issue.get('severity', 'medium'),
                        'line': issue.get('line', 1),
                        'message': issue.get('message', 'Issue detected'),
                        'suggestion': issue.get('suggestion', 'Review and fix'),
                        'file': file_path
                    })
        
        except json.JSONDecodeError:
            # Failed to parse JSON response
            pass
        
        return issues
