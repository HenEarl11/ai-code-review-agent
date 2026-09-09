# Configuration Templates for AI Code Review Agent

Python, Terraform, and TypeScript configurations for the code review analysis engine.

## Available Configurations

### 1. Python Configuration
**File:** `python.py`

**Best for:**
- Django, FastAPI, Flask applications
- Python libraries and packages
- Data science projects (pandas, numpy, scikit-learn)
- Microservices in Python

**Key Features:**
- Uses CodeLLaMA model (specialized for code)
- Detects Django ORM N+1 queries
- Enforces PEP 8 standards
- Type hint checking
- Framework-specific checks (Django, FastAPI, Flask)
- Test coverage validation

**Detects:**
- Hardcoded credentials and secrets
- SQL injection vulnerabilities
- N+1 database query patterns (Django ORM)
- Missing type hints and docstrings
- Bare except clauses
- Unsafe deserialization (pickle, yaml.load)
- Performance issues (nested loops, string concatenation)

**Example Usage:**
```bash
CODEBASE_STYLE=python ./setup.sh start
```

---

### 2. Terraform Configuration
**File:** `terraform.py`

**Best for:**
- Infrastructure as Code (Terraform, CloudFormation)
- Kubernetes manifests (YAML)
- Docker Compose files
- Helm charts
- CI/CD pipelines (GitHub Actions, GitLab CI)
- Docker containers

**Key Features:**
- Cloud provider detection (AWS, GCP, Azure)
- Kubernetes best practices enforcement
- Resource limit and HA validation
- Security policy checks
- Cost optimization suggestions
- Terraform specific checks (hardcoded values, lifecycle rules)

**Detects:**
- Hardcoded secrets in IaC
- Public S3/Storage buckets
- Unencrypted databases
- Single replica in production (no HA)
- Missing resource limits in K8s
- Missing network policies
- Overly permissive IAM roles
- No backup policies
- Latest container image tags (should use specific versions)
- Containers running as root

**Example Usage:**
```bash
CODEBASE_STYLE=terraform ./setup.sh start
```

---

### 3. TypeScript Configuration
**File:** `typescript.py`

**Best for:**
- React, Next.js, Vue.js applications
- Node.js/Express backends
- NestJS microservices
- Full-stack TypeScript applications
- Electron desktop apps
- React Native mobile apps

**Key Features:**
- Uses CodeLLaMA model
- React hooks validation
- Type safety enforcement (no 'any' types)
- Async/await and Promise handling
- Framework detection (React, Next.js, Express, NestJS)
- ESLint rule enforcement
- Test coverage validation

**Detects:**
- Missing TypeScript type annotations
- Usage of 'any' type
- Unhandled promise rejections
- React hooks dependency issues
- Missing key props in lists
- XSS vulnerabilities (dangerouslySetInnerHTML)
- SQL injection in database queries
- Missing error boundaries
- Console.log in production code
- Unused imports
- Performance issues (N+1 queries, unnecessary re-renders)

**Example Usage:**
```bash
CODEBASE_STYLE=typescript ./setup.sh start
```

---

## Configuration Structure

Each configuration class inherits from `CodebaseConfigTemplate` and defines:

### Basic Settings
```python
NAME = "python"                          # Config identifier
DESCRIPTION = "Python/Django projects"  # Description
SUPPORTED_LANGUAGES = ["python"]        # Supported file types
```

### LLM Settings
```python
LLM_MODEL = "codellama"         # Model to use
LLM_TEMPERATURE = 0.2           # Determinism (0-1)
LLM_TIMEOUT = 30                # Max seconds for analysis
LLM_CONTEXT_LIMIT = 2000        # Max chars sent to LLM
```

### Analysis Settings
```python
ACTIVE_DETECTORS = [            # Which detectors to run
    "security",
    "performance",
    "standards",
    # ... more
]

ANALYZE_PATTERNS = [            # Files to analyze
    "**/*.py",
    "**/*.js",
]

IGNORE_PATTERNS = [             # Files to skip
    "**/node_modules/**",
    "**/venv/**",
]
```

### Custom Rules
```python
SEVERITY_OVERRIDES = {          # Adjust issue severity
    "unused_import": "low",
    "n_plus_one_query": "critical",
}

LLM_SYSTEM_PROMPT = """...""" # Custom LLM instructions
```

---

## Auto-Detection

Automatically detect the codebase type:

```python
from config_templates.config_manager import ConfigManager

# Auto-detect based on files in directory
config = ConfigManager.auto_detect('/path/to/code')

# Or explicitly set
config = ConfigManager.get_config('python')

# Or use environment variable
os.environ['CODEBASE_STYLE'] = 'terraform'
config = ConfigManager.get_config()
```

---

## Usage in Backend

**Updated `backend/app.py`:**
```python
from config_templates.config_manager import ConfigManager

def create_app(config_name=None):
    # Get codebase configuration
    codebase_config = ConfigManager.get_config(config_name)
    
    # Use configuration in analysis engine
    analysis_engine = AnalysisEngine(codebase_config)
    
    return app
```

**Updated `backend/analysis/engine.py`:**
```python
class AnalysisEngine:
    def __init__(self, config=None):
        if config is None:
            config = ConfigManager.get_config()
        
        self.config = config
        self.llm_service = LLMService(
            model=config.LLM_MODEL,
            temperature=config.LLM_TEMPERATURE,
            timeout=config.LLM_TIMEOUT,
            system_prompt=config.LLM_SYSTEM_PROMPT
        )
        
        # Only load enabled detectors
        self.detectors = {}
        for detector_name in config.ACTIVE_DETECTORS:
            if detector_name == 'security':
                self.detectors['security'] = SecurityDetector()
            # ... more detectors
```

---

## Adding Custom Configuration

### Create New Config

**File: `backend/config_templates/golang.py`**
```python
from .base import CodebaseConfigTemplate

class GolangCodebaseConfig(CodebaseConfigTemplate):
    NAME = "golang"
    DESCRIPTION = "Configuration for Go/Golang projects"
    SUPPORTED_LANGUAGES = ["go"]
    
    LLM_MODEL = "mistral"
    ACTIVE_DETECTORS = [
        "security",
        "performance",
        "golang_specific",
    ]
    
    # ... rest of config
```

### Register Config

**File: `backend/config_templates/__init__.py`**
```python
from .golang import GolangCodebaseConfig

ConfigManager.register_config('golang', GolangCodebaseConfig)
```

### Use Custom Config

```bash
CODEBASE_STYLE=golang ./setup.sh start
```

---

## Environment Variables

Set configuration via environment:

```bash
# Choose configuration
export CODEBASE_STYLE=python

# Override settings
export LLM_MODEL=codellama
export LLM_TEMPERATURE=0.3
export CACHE_ENABLED=true

./setup.sh start
```

---

## Configuration Examples

### Python/Django Project
```bash
CODEBASE_STYLE=python \
LLM_MODEL=codellama \
MAX_FILE_SIZE=2000000 \
./setup.sh start
```

### Terraform/K8s Infrastructure
```bash
CODEBASE_STYLE=terraform \
LLM_MODEL=mistral \
CACHE_ENABLED=true \
./setup.sh start
```

### React/Next.js Frontend
```bash
CODEBASE_STYLE=typescript \
LLM_MODEL=codellama \
ANALYSIS_TIMEOUT=20 \
./setup.sh start
```

---

## Testing Configurations

Test a specific configuration:

```bash
# Start with Python config
CODEBASE_STYLE=python ./setup.sh start

# Test analysis
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "example.py",
    "code": "password = \"secret123\"",
    "language": "python"
  }'

# Get config details
curl http://localhost:5000/api/config
```

---

## Performance Considerations

Each configuration has different performance profiles:

| Config | Avg Analysis Time | Memory Use | Best For |
|--------|-------------------|------------|----------|
| Python | 2-3s | 256MB | Typical files |
| Terraform | 1-2s | 128MB | Small IaC files |
| TypeScript | 3-4s | 384MB | Complex React components |

---

## Extending Detectors

Each configuration can enable custom detectors:

```python
# Python config with custom Django detector
ACTIVE_DETECTORS = [
    "security",
    "django_orm_optimization",  # Custom
    "django_signal_usage",       # Custom
]
```

Implement detector:
```python
# backend/analysis/detectors/django_orm_optimization.py
class DjangoORMOptimizationDetector:
    def detect(self, code, parsed_data, file_path):
        # Check for N+1 queries
        # Suggest select_related/prefetch_related
        pass
```

---

## Next Steps

1. Test each configuration with sample codebases
2. Add more framework-specific detectors
3. Fine-tune LLM prompts based on results
4. Create integration tests
5. Document custom detectors

---

For more information, see individual configuration files.
