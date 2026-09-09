import re
from typing import List, Dict

class AntiPatternDetector:
    """Detect code anti-patterns"""
    
    def detect(self, code: str, parsed_data: dict, file_path: str) -> List[Dict]:
        """Detect anti-patterns in code"""
        issues = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Magic numbers
            if re.search(r'=\s*\d{3,}(?!\d)', line) and 'const' not in line.lower() and '0x' not in line:
                issues.append({
                    'type': 'antipattern',
                    'subtype': 'magic_number',
                    'severity': 'low',
                    'line': line_num,
                    'message': 'Magic number detected',
                    'suggestion': 'Extract magic number to a named constant',
                    'file': file_path
                })
            
            # Bare except
            if re.search(r'except\s*:', line):
                issues.append({
                    'type': 'antipattern',
                    'subtype': 'bare_except',
                    'severity': 'high',
                    'line': line_num,
                    'message': 'Bare except clause detected',
                    'suggestion': 'Catch specific exceptions instead of using bare except',
                    'file': file_path
                })
            
            # Missing null check
            if re.search(r'\w+\.\w+\(', line) and '==' not in line and 'is not None' not in line:
                issues.append({
                    'type': 'antipattern',
                    'subtype': 'potential_null_dereference',
                    'severity': 'medium',
                    'line': line_num,
                    'message': 'Potential null dereference',
                    'suggestion': 'Add null check before accessing object method/property',
                    'file': file_path
                })
        
        return issues
