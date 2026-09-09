"""Base configuration template for all codebases"""
from enum import Enum
from typing import List, Dict, Optional

class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class CodebaseConfigTemplate:
    """Base template for codebase-specific configurations"""
    
    # Basic info
    NAME: str = "generic"
    DESCRIPTION: str = "Generic codebase configuration"
    SUPPORTED_LANGUAGES: List[str] = ["python", "javascript", "typescript"]
    
    # LLM Configuration
    LLM_MODEL: str = "mistral"  # Model to use
    LLM_TEMPERATURE: float = 0.3  # 0-1, lower = more deterministic
    LLM_TIMEOUT: int = 30  # seconds
    LLM_CONTEXT_LIMIT: int = 2000  # max chars to send to LLM
    
    # Enabled detectors
    ACTIVE_DETECTORS: List[str] = [
        "security",
        "performance",
        "standards",
        "test_coverage",
        "antipattern",
    ]
    
    # File patterns to analyze
    ANALYZE_PATTERNS: List[str] = [
        "**/*.py",
        "**/*.js",
        "**/*.ts",
        "**/*.tsx",
    ]
    
    # Patterns to ignore
    IGNORE_PATTERNS: List[str] = [
        "**/node_modules/**",
        "**/__pycache__/**",
        "**/venv/**",
        "**/dist/**",
        "**/build/**",
        "**/.git/**",
    ]
    
    # Severity overrides (codebase-specific)
    SEVERITY_OVERRIDES: Dict[str, str] = {}
    
    # Custom LLM system prompt
    LLM_SYSTEM_PROMPT: str = """You are a code reviewer analyzing code for issues.
    
Analyze the provided code and return a JSON array of detected issues.
Each issue should have: line, severity (critical/high/medium/low), type, message, suggestion.
    
Focus on:
- Security vulnerabilities
- Performance problems
- Code standards violations
- Missing tests
- Anti-patterns and potential bugs
    
Return ONLY valid JSON."""
    
    # Analysis settings
    MAX_FILE_SIZE: int = 1000000  # 1MB
    ANALYSIS_TIMEOUT: int = 30  # seconds per file
    CACHE_ENABLED: bool = True
    
    # Report settings
    REPORT_FORMAT: str = "json"  # json, html, markdown
    INCLUDE_SUGGESTIONS: bool = True
    MIN_SEVERITY_TO_REPORT: str = "low"  # Only report this severity and above
    
    # Integration settings
    JIRA_ENABLED: bool = True
    JIRA_ISSUE_TYPE: str = "Task"
    AUTO_CREATE_ISSUES: bool = False  # Manual review before creating
    
    @classmethod
    def to_dict(cls) -> Dict:
        """Convert configuration to dictionary"""
        return {
            'name': cls.NAME,
            'description': cls.DESCRIPTION,
            'supported_languages': cls.SUPPORTED_LANGUAGES,
            'llm_model': cls.LLM_MODEL,
            'llm_temperature': cls.LLM_TEMPERATURE,
            'llm_timeout': cls.LLM_TIMEOUT,
            'active_detectors': cls.ACTIVE_DETECTORS,
            'analyze_patterns': cls.ANALYZE_PATTERNS,
            'ignore_patterns': cls.IGNORE_PATTERNS,
            'severity_overrides': cls.SEVERITY_OVERRIDES,
            'cache_enabled': cls.CACHE_ENABLED,
            'jira_enabled': cls.JIRA_ENABLED,
        }
