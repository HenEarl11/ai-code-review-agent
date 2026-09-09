import re
from typing import List, Dict

class TestCoverageDetector:
    """Detect missing test coverage"""
    
    def detect(self, code: str, parsed_data: dict, file_path: str) -> List[Dict]:
        """Detect missing test coverage"""
        issues = []
        
        # Check if this is a test file
        if 'test' in file_path.lower():
            return issues
        
        functions = parsed_data.get('functions', [])
        imports = parsed_data.get('imports', [])
        
        # Check if file imports test modules
        has_test_imports = any('test' in imp.get('module', '').lower() for imp in imports if imp.get('type') == 'from')
        
        # If no test imports found and file has functions
        if not has_test_imports and functions:
            issues.append({
                'type': 'test_coverage',
                'subtype': 'no_tests',
                'severity': 'medium',
                'line': 1,
                'message': 'No test imports found for this module',
                'suggestion': 'Consider adding unit tests for public functions',
                'file': file_path
            })
        
        # Check for complex functions without docstrings
        for func in functions:
            if func.get('args') and len(func.get('args', [])) > 3:
                issues.append({
                    'type': 'test_coverage',
                    'subtype': 'complex_function',
                    'severity': 'low',
                    'line': func['line'],
                    'message': f'Function {func["name"]} has multiple parameters - ensure it is well tested',
                    'suggestion': 'Add unit tests covering different parameter combinations',
                    'file': file_path
                })
        
        return issues
