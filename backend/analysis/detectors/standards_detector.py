import re
from typing import List, Dict

class StandardsDetector:
    """Detect code standards violations"""
    
    def detect(self, code: str, parsed_data: dict, file_path: str) -> List[Dict]:
        """Detect code standards violations"""
        issues = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Check line length (PEP 8: max 79 chars)
            if len(line) > 79:
                issues.append({
                    'type': 'standard',
                    'subtype': 'line_too_long',
                    'severity': 'low',
                    'line': line_num,
                    'message': f'Line too long ({len(line)} > 79 characters)',
                    'suggestion': 'Break line into multiple lines or reduce length',
                    'file': file_path
                })
            
            # Check for unused imports
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                import_name = re.search(r'(?:from|import)\s+([\w.]+)', line)
                if import_name:
                    module = import_name.group(1).split('.')[0]
                    if not self._is_used(module, code, line_num):
                        issues.append({
                            'type': 'standard',
                            'subtype': 'unused_import',
                            'severity': 'low',
                            'line': line_num,
                            'message': f'Unused import: {module}',
                            'suggestion': 'Remove unused import',
                            'file': file_path
                        })
            
            # Check naming conventions
            if 'def ' in line:
                func_name = re.search(r'def\s+(\w+)', line)
                if func_name and self._is_invalid_name(func_name.group(1)):
                    issues.append({
                        'type': 'standard',
                        'subtype': 'invalid_name',
                        'severity': 'low',
                        'line': line_num,
                        'message': f'Invalid function name: {func_name.group(1)}',
                        'suggestion': 'Use snake_case for function names',
                        'file': file_path
                    })
        
        return issues
    
    def _is_used(self, module: str, code: str, skip_line: int) -> bool:
        """Check if module/variable is used in code"""
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if i != skip_line - 1 and module in line:
                return True
        return False
    
    def _is_invalid_name(self, name: str) -> bool:
        """Check if name violates snake_case convention"""
        return bool(re.search(r'[A-Z]', name)) and '_' not in name
