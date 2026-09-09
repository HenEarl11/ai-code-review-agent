"""TypeScript/Node.js codebase configuration"""
from .base import CodebaseConfigTemplate, Severity
from typing import List, Dict

class TypeScriptCodebaseConfig(CodebaseConfigTemplate):
    """Configuration optimized for TypeScript, React, Next.js, and Node.js projects"""
    
    NAME = "typescript"
    DESCRIPTION = "Configuration for TypeScript, React, Next.js, Express, and Node.js projects"
    SUPPORTED_LANGUAGES = ["typescript", "javascript", "jsx", "tsx"]
    
    # Use CodeLLaMA for JavaScript/TypeScript
    LLM_MODEL = "codellama"
    LLM_TEMPERATURE = 0.2
    
    # TypeScript-specific detectors
    ACTIVE_DETECTORS = [
        "security",
        "performance",
        "standards",
        "test_coverage",
        "antipattern",
        "typescript_specific",
        "react_specific",
        "async_await_issues",
        "type_safety",
    ]
    
    # Analyze TypeScript/JavaScript files
    ANALYZE_PATTERNS = [
        "**/*.ts",
        "**/*.tsx",
        "**/*.js",
        "**/*.jsx",
        "**/pages/**/*.ts",
        "**/pages/**/*.tsx",
        "**/src/**/*.ts",
        "**/src/**/*.tsx",
        "**/components/**/*.ts",
        "**/components/**/*.tsx",
    ]
    
    # TypeScript-specific ignore patterns
    IGNORE_PATTERNS = [
        "**/node_modules/**",
        "**/dist/**",
        "**/build/**",
        "**/.next/**",
        "**/out/**",
        "**/__pycache__/**",
        "**/.venv/**",
        "**/.git/**",
        "**/coverage/**",
        "**/logs/**",
    ]
    
    # Override severities for TypeScript
    SEVERITY_OVERRIDES = {
        "missing_type_annotations": Severity.MEDIUM,
        "any_type_usage": Severity.HIGH,
        "unused_imports": Severity.LOW,
        "missing_error_handling": Severity.HIGH,
        "unhandled_promise_rejection": Severity.CRITICAL,
        "missing_async_await": Severity.MEDIUM,
        "callback_hell": Severity.MEDIUM,
        "react_missing_key": Severity.HIGH,
        "react_missing_dependency": Severity.HIGH,
        "sql_injection": Severity.CRITICAL,
        "hardcoded_credentials": Severity.CRITICAL,
        "xss_vulnerability": Severity.CRITICAL,
        "csrf_vulnerability": Severity.HIGH,
    }
    
    # TypeScript-specific LLM prompt
    LLM_SYSTEM_PROMPT = """You are an expert TypeScript/JavaScript code reviewer.

ANALYZE for:

1. TYPE SAFETY ISSUES:
   - Usage of 'any' type (use unknown or specific types)
   - Missing type annotations on function parameters/returns
   - Implicit 'any' types
   - Type casting instead of proper typing
   - Missing interface/type definitions
   - Not using strict mode in tsconfig.json

2. ASYNC/AWAIT & PROMISES:
   - Unhandled promise rejections
   - Missing await on promises
   - Callback hell (use async/await instead)
   - Floating promises not awaited
   - Missing try/catch blocks
   - Promise.all() error handling
   - Race conditions in concurrent code

3. REACT-SPECIFIC:
   - Missing key prop in lists
   - useEffect missing dependency array
   - useCallback/useMemo not used when needed
   - State mutations (mutating state directly)
   - Missing useCallback for event handlers
   - Stale closure bugs
   - Props drilling instead of context
   - Large components needing refactoring

4. SECURITY ISSUES:
   - SQL injection in database queries
   - XSS vulnerabilities (dangerouslySetInnerHTML, eval)
   - CSRF token not validated
   - Hardcoded API keys/secrets
   - Insecure random number generation
   - Missing input validation
   - Path traversal vulnerabilities
   - CORS misconfiguration

5. PERFORMANCE ISSUES:
   - N+1 database queries
   - Large bundle size
   - Unnecessary re-renders in React
   - Missing memoization
   - Inefficient algorithms
   - Memory leaks
   - Unoptimized images
   - Dead code not removed

6. TESTING:
   - Missing unit tests
   - Missing integration tests
   - Low test coverage
   - Untested error paths
   - No snapshot tests for components
   - Missing E2E tests

7. CODE STANDARDS:
   - Naming conventions (camelCase for vars/functions, PascalCase for components/classes)
   - Line length (max 100 chars recommended)
   - Unused imports
   - Unused variables
   - Console.log left in production code
   - TODO/FIXME comments without context

8. ERROR HANDLING:
   - Missing error boundaries in React
   - Unhandled errors in async functions
   - Generic error messages
   - No logging strategy
   - Missing null/undefined checks

9. NEXT.JS SPECIFIC:
   - API routes not validating input
   - Missing API error handling
   - Not using getStaticProps when possible
   - Memory leaks in middleware
   - Image optimization not used

10. EXPRESS/NODE.JS SPECIFIC:
    - Missing middleware ordering
    - Unhandled route errors
    - Missing request validation
    - SQL injection in queries
    - Not using helmet.js for security headers
    - Missing rate limiting

Return ONLY valid JSON array with: line, severity, type, message, suggestion."""
    
    # TypeScript-specific settings
    REQUIRE_STRICT_MODE = True         # Require strict: true in tsconfig
    REQUIRE_TYPE_ANNOTATIONS = True    # Require function annotations
    REQUIRE_ERROR_HANDLING = True       # Require try/catch for async
    REQUIRE_TESTS = True               # Require test files
    CHECK_REACT_HOOKS = True           # Check React hooks rules
    CHECK_BUNDLE_SIZE = True           # Warn about large bundles
    MIN_TEST_COVERAGE = 80             # % coverage required
    
    # Framework detection
    FRAMEWORK_HINTS = {
        "react": ["react", "from 'react'", "from \"react\"", "JSX", "<Component"],
        "next": ["next", "next/", "getStaticProps", "getServerSideProps"],
        "express": ["express", "app.get", "app.post", "@app."],
        "nestjs": ["@nestjs", "@Controller", "@Injectable"],
        "vue": ["vue", "<template>", "defineComponent"],
        "svelte": ["svelte", "<script>"],
    }
    
    # Framework-specific checks
    FRAMEWORK_SPECIFIC_CHECKS = {
        "react": [
            "react_hooks_rules",
            "react_component_naming",
            "react_prop_types",
            "react_key_prop",
            "react_performance",
            "react_accessibility",
        ],
        "next": [
            "next_data_fetching",
            "next_image_optimization",
            "next_link_usage",
            "next_api_routes",
            "next_performance",
        ],
        "express": [
            "express_error_handling",
            "express_middleware_order",
            "express_validation",
            "express_security",
            "express_rate_limiting",
        ],
        "nestjs": [
            "nestjs_decorator_usage",
            "nestjs_dependency_injection",
            "nestjs_error_handling",
            "nestjs_validation",
        ],
    }
    
    # Linting rules to check
    ESLINT_RULES_TO_ENFORCE = [
        "@typescript-eslint/no-explicit-any",
        "@typescript-eslint/explicit-function-return-types",
        "no-console",
        "no-unused-vars",
        "no-floating-promises",
        "require-await",
        "prefer-const",
        "react/jsx-key",
        "react-hooks/rules-of-hooks",
        "react-hooks/exhaustive-deps",
    ]
    
    @classmethod
    def to_dict(cls) -> Dict:
        config = super().to_dict()
        config.update({
            "require_strict_mode": cls.REQUIRE_STRICT_MODE,
            "require_type_annotations": cls.REQUIRE_TYPE_ANNOTATIONS,
            "require_error_handling": cls.REQUIRE_ERROR_HANDLING,
            "require_tests": cls.REQUIRE_TESTS,
            "check_react_hooks": cls.CHECK_REACT_HOOKS,
            "min_test_coverage": cls.MIN_TEST_COVERAGE,
        })
        return config
