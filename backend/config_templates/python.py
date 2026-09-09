"""Python/Django codebase configuration"""
from .base import CodebaseConfigTemplate, Severity
from typing import List, Dict

class PythonCodebaseConfig(CodebaseConfigTemplate):
    """Configuration optimized for Python/Django/FastAPI codebases"""
    
    NAME = "python"
    DESCRIPTION = "Configuration for Python, Django, FastAPI, and Flask projects"
    SUPPORTED_LANGUAGES = ["python"]
    
    # Use CodeLLaMA for better Python understanding
    LLM_MODEL = "codellama"
    LLM_TEMPERATURE = 0.2  # More deterministic for Python
    
    # Python-specific detectors
    ACTIVE_DETECTORS = [
        "security",
        "performance",
        "standards",  # PEP 8
        "test_coverage",
        "antipattern",
        "python_specific",
        "django_orm_optimization",
    ]
    
    # Only analyze Python files
    ANALYZE_PATTERNS = [
        "**/*.py",
    ]
    
    # Python-specific ignore patterns
    IGNORE_PATTERNS = [
        "**/migrations/**",
        "**/__pycache__/**",
        "**/venv/**",
        "**/env/**",
        "**/.venv/**",
        "**/dist/**",
        "**/build/**",
        "**/*.egg-info/**",
        "**/node_modules/**",  # Sometimes in monorepos
    ]
    
    # Override severities for Python standards
    SEVERITY_OVERRIDES = {
        "unused_import": Severity.LOW,
        "line_too_long": Severity.LOW,
        "missing_docstring": Severity.LOW,
        "invalid_name": Severity.LOW,
        "missing_type_hints": Severity.MEDIUM,
        "bare_except": Severity.HIGH,
        "n_plus_one_query": Severity.CRITICAL,  # Django
        "sql_injection": Severity.CRITICAL,
        "hardcoded_credentials": Severity.CRITICAL,
    }
    
    # Python-specific LLM prompt
    LLM_SYSTEM_PROMPT = """You are an expert Python code reviewer.

ANALYZE for:
1. Security Issues:
   - Hardcoded credentials, API keys, passwords
   - SQL injection via raw queries or f-strings
   - Unsafe deserialization (pickle, yaml.load)
   - XSS vulnerabilities
   - Command injection via subprocess/os.system

2. Performance Issues:
   - N+1 database queries (especially Django ORM)
   - Nested loops causing O(n²) complexity
   - String concatenation in loops
   - Memory leaks (unclosed resources)
   - Inefficient list comprehensions

3. Code Standards (PEP 8):
   - Function/variable naming (snake_case)
   - Line length (max 79 chars)
   - Unused imports and variables
   - Missing docstrings
   - Type hints for complex functions

4. Django-Specific (if applicable):
   - N+1 query problems - suggest select_related/prefetch_related
   - Signal misuse
   - Middleware ordering
   - ORM anti-patterns
   - Missing database indexes

5. Testing:
   - Missing unit tests for functions
   - Inadequate test coverage
   - Missing edge case tests
   - Untested error paths

6. Anti-Patterns:
   - Bare except clauses
   - Magic numbers without constants
   - Missing null/None checks
   - Mutable default arguments
   - Global state usage

Return ONLY valid JSON array with: line, severity, type, message, suggestion."""
    
    # Python-specific settings
    MIN_TEST_COVERAGE = 80  # %
    CHECK_TYPE_HINTS = True
    CHECK_DOCSTRINGS = True
    CHECK_PEP8 = True
    CHECK_DJANGO_SIGNALS = True
    CHECK_N_PLUS_ONE = True
    CHECK_ASYNC_VIEWS = True
    
    # Framework detection
    FRAMEWORK_HINTS = {
        "django": ["django", "from django", "import django"],
        "fastapi": ["fastapi", "from fastapi", "@app.post"],
        "flask": ["flask", "from flask", "@app.route"],
        "sqlalchemy": ["sqlalchemy", "from sqlalchemy"],
    }
    
    # Custom rules by framework
    FRAMEWORK_SPECIFIC_CHECKS = {
        "django": [
            "django_orm_optimization",
            "django_signal_usage",
            "django_middleware_order",
            "django_async_views",
        ],
        "fastapi": [
            "fastapi_dependency_injection",
            "fastapi_response_model",
            "fastapi_validation",
        ],
        "flask": [
            "flask_blueprint_usage",
            "flask_error_handling",
            "flask_context_management",
        ],
    }
    
    @classmethod
    def to_dict(cls) -> Dict:
        config = super().to_dict()
        config.update({
            "min_test_coverage": cls.MIN_TEST_COVERAGE,
            "check_type_hints": cls.CHECK_TYPE_HINTS,
            "check_docstrings": cls.CHECK_DOCSTRINGS,
            "check_pep8": cls.CHECK_PEP8,
            "check_django_signals": cls.CHECK_DJANGO_SIGNALS,
            "check_n_plus_one": cls.CHECK_N_PLUS_ONE,
        })
        return config
