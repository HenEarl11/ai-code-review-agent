import ast
import os
from .parsers.python_parser import PythonParser
from .detectors.security_detector import SecurityDetector
from .detectors.performance_detector import PerformanceDetector
from .detectors.standards_detector import StandardsDetector
from .detectors.test_coverage_detector import TestCoverageDetector
from .detectors.antipattern_detector import AntiPatternDetector
from .llm.inference import LLMService

class AnalysisEngine:
    """Main analysis orchestrator"""
    
    def __init__(self):
        self.parsers = {
            'python': PythonParser()
        }
        
        self.detectors = {
            'security': SecurityDetector(),
            'performance': PerformanceDetector(),
            'standards': StandardsDetector(),
            'test_coverage': TestCoverageDetector(),
            'antipattern': AntiPatternDetector()
        }
        
        self.llm_service = LLMService()
    
    def analyze(self, code, file_path, language='python', codebase_style: str = None):
        """
        Analyze code and return detected issues
        
        Args:
            code (str): Code content to analyze
            file_path (str): Path to the file
            language (str): Programming language
        
        Returns:
            dict: Analysis results with detected issues
        """
        results = {
            'file_path': file_path,
            'language': language,
            'issues': [],
            'summary': {
                'total_issues': 0,
                'by_severity': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
                'by_type': {}
            }
        }
        
        try:
            # Parse code
            parser = self.parsers.get(language)
            if not parser:
                return {'error': f'Language {language} not supported'}
            
            parsed_data = parser.parse(code)
            
            # Run pattern-based detectors
            all_issues = []
            for detector_name, detector in self.detectors.items():
                issues = detector.detect(code, parsed_data, file_path)
                all_issues.extend(issues)
            
            # Get LLM-based analysis (pass codebase style so prompts/templates can adapt)
            llm_issues = self.llm_service.analyze(code, file_path, parsed_data, codebase_style=codebase_style)
            all_issues.extend(llm_issues)
            
            # Deduplicate and aggregate
            seen = set()
            for issue in all_issues:
                issue_key = (issue['line'], issue['message'])
                if issue_key not in seen:
                    results['issues'].append(issue)
                    seen.add(issue_key)
                    
                    # Update summary
                    severity = issue.get('severity', 'low')
                    results['summary']['by_severity'][severity] += 1
                    issue_type = issue.get('type', 'unknown')
                    results['summary']['by_type'][issue_type] = results['summary']['by_type'].get(issue_type, 0) + 1
            
            results['summary']['total_issues'] = len(results['issues'])
        
        except Exception as e:
            results['error'] = str(e)
        
        return results
