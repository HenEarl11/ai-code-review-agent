import re
from typing import List, Dict

class PerformanceDetector:
    """Detect performance issues in code"""
    
    def detect(self, code: str, parsed_data: dict, file_path: str) -> List[Dict]:
        """Detect performance issues in code"""
        issues = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Detect nested loops
            indent_level = len(line) - len(line.lstrip())
            if 'for' in line or 'while' in line:
                # Check next lines for more loops
                if line_num < len(lines):
                    next_line = lines[line_num]
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if ('for' in next_line or 'while' in next_line) and next_indent > indent_level:
                        issues.append({
                            'type': 'performance',
                            'subtype': 'nested_loops',
                            'severity': 'medium',
                            'line': line_num,
                            'message': 'Nested loops detected - potential O(n²) complexity',
                            'suggestion': 'Consider optimization or use data structures like sets/dicts',
                            'file': file_path
                        })
            
            # Detect string concatenation in loops
            if ('for' in line or 'while' in line) and any('+' in l and '"' in l for l in lines[line_num:min(line_num+5, len(lines))]):
                issues.append({
                    'type': 'performance',
                    'subtype': 'string_concatenation',
                    'severity': 'medium',
                    'line': line_num,
                    'message': 'String concatenation in loop detected',
                    'suggestion': 'Use list and join() instead of string concatenation',
                    'file': file_path
                })
            
            # Detect list comprehension vs append
            if '.append(' in line and 'for' in lines[max(0, line_num-5):line_num]:
                issues.append({
                    'type': 'performance',
                    'subtype': 'inefficient_list_building',
                    'severity': 'low',
                    'line': line_num,
                    'message': 'Consider using list comprehension',
                    'suggestion': 'Replace loop with list comprehension for better performance',
                    'file': file_path
                })
        
        return issues
