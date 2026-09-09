import re
from typing import List, Dict

class SecurityDetector:
    """Detect security vulnerabilities in code"""
    
    PATTERNS = {
        'hardcoded_credentials': (
            r"(?i)(password|secret|token|api[_-]?key|auth[_-]?token)\s*=\s*['\"]([^'\"]+)['\"]",
            'critical',
            'Hardcoded credentials detected'
        ),
        'sql_injection': (
            r"(execute|query)\s*\(\s*['\"].*\{.*\}['\"]|f['\"].*{.*}['\"].*sql",
            'high',
            'Potential SQL injection vulnerability'
        ),
        'command_injection': (
            r"(exec|eval|system|os\.popen|subprocess\.call)\s*\(.*\+.*\)",
            'high',
            'Potential command injection vulnerability'
        ),
        'weak_random': (
            r"(random\.randint|random\.choice|random\.shuffle)",
            'medium',
            'Using weak random for security-sensitive operations'
        ),
        'unsafe_deserialization': (
            r"(pickle\.load|yaml\.load|json\.load)\s*\(",
            'high',
            'Unsafe deserialization detected'
        )
    }
    
    def detect(self, code: str, parsed_data: dict, file_path: str) -> List[Dict]:
        """Detect security issues in code"""
        issues = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for pattern_name, (pattern, severity, message) in self.PATTERNS.items():
                if re.search(pattern, line):
                    issues.append({
                        'type': 'security',
                        'subtype': pattern_name,
                        'severity': severity,
                        'line': line_num,
                        'message': message,
                        'suggestion': f'Review and remove {pattern_name}',
                        'file': file_path
                    })
        
        return issues
