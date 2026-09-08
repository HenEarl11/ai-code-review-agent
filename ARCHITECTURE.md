# AI Code Review Agent - Architecture & Design

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Developer Workflow                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────┐         ┌──────────────────┐              │
│  │  VS Code Editor  │         │   File System    │              │
│  │   + Extension    │◄────────│  (Code Files)    │              │
│  └────────┬─────────┘         └──────────────────┘              │
│           │                                                       │
│           │ (Watch file changes / On-demand analysis)            │
│           ▼                                                       │
│  ┌──────────────────────────────────────────────┐               │
│  │   VS Code Extension (TypeScript/JavaScript)  │               │
│  │  - File watcher                              │               │
│  │  - UI for displaying issues                  │               │
│  │  - Quick fix suggestions                     │               │
│  └────────────────┬─────────────────────────────┘               │
│                   │ (LSP / IPC / HTTP)                           │
└───────────────────┼───────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│              Local Analysis Engine (Backend)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────────────────────────────┐                │
│  │   Code Review Agent (Python/Node.js)       │                │
│  │  - Entry point for analysis requests       │                │
│  │  - Orchestrates analysis pipeline          │                │
│  └─────────────────┬────────────────────────┘                 │
│                    │                                             │
│  ┌─────────────────┴───────────────────────────┐                │
│  │                                             │                │
│  ▼                                             ▼                │
│  ┌──────────────────┐          ┌──────────────────────┐         │
│  │ Code Parsers     │          │  Issue Detectors     │         │
│  │ - AST parsers    │          │  - Security scanner  │         │
│  │ - Language-      │          │  - Performance       │         │
│  │   specific       │          │    analyzer          │         │
│  │   analysis       │          │  - Code standards    │         │
│  └──────────────────┘          │  - Test coverage     │         │
│                                 │  - Anti-patterns     │         │
│                                 └──────────────────────┘         │
│                    │                    │                        │
│  ┌─────────────────┴────────────────────┴──────────┐            │
│  │                                                  │            │
│  ▼                                                  ▼            │
│  ┌──────────────────────────────────────────────┐              │
│  │   LLM Service (Ministack / Ollama)           │              │
│  │  - Local model inference                     │              │
│  │  - Context-aware analysis                    │              │
│  │  - Severity classification                   │              │
│  └──────────────────────────────────────────────┘              │
│                    │                                             │
│                    ▼                                             │
│  ┌──────────────────────────────────────────────┐              │
│  │   Results Aggregator & Formatter             │              │
│  │  - Consolidate findings                      │              │
│  │  - Format for IDE and Jira                   │              │
│  │  - Cache results (SQLite)                    │              │
│  └──────────────────────────────────────────────┘              │
│                                                                   │
└───────────────────┬──────────────────────────┬────────────────────┘
                    │                          │
         ┌──────────┘                          └──────────┐
         │                                                 │
         ▼                                                 ▼
    ┌─────────────┐                              ┌──────────────┐
    │ SQLite DB   │                              │ Jira Service │
    │ (Cache/     │                              │ (REST API)   │
    │  History)   │                              │              │
    └─────────────┘                              └──────────────┘
                                                        │
                                                        ▼
                                                  ┌──────────────┐
                                                  │ Jira Board   │
                                                  │ (Issues)     │
                                                  └──────────────┘
```

## Component Details

### 1. VS Code Extension
**Responsibility**: IDE UI layer and user interaction

```
files/
├── package.json              # Extension metadata
├── src/
│   ├── extension.ts         # Main extension entry
│   ├── commands/
│   │   ├── analyzeFile.ts   # On-demand analysis
│   │   └── analyzePR.ts     # PR analysis command
│   ├── providers/
│   │   ├── diagnostics.ts   # Display issues in editor
│   │   └── codeActions.ts   # Quick fixes
│   ├── webview/
│   │   ├── panel.ts         # Results panel
│   │   └── dashboard.ts     # Issue dashboard
│   └── utils/
│       ├── client.ts        # Backend communication
│       └── config.ts        # Extension settings
└── media/
    └── icons/               # UI icons
```

**Key Features**:
- Watch for file changes and trigger analysis
- Display inline diagnostics (red squiggles)
- Show severity indicators (error/warning/info)
- Quick fix suggestions
- Analysis results panel
- Settings panel (model selection, issue categories)

### 2. Backend Analysis Engine
**Responsibility**: Core code analysis and AI inference

```
backend/
├── main.py (or index.js)    # Server entry point
├── app.py                   # Flask/Express app
├── api/
│   ├── routes.py           # REST endpoints
│   │   ├── /analyze        # POST: analyze code
│   │   ├── /issues         # GET: list issues
│   │   └── /jira-sync      # POST: sync to Jira
│   └── models.py           # Request/response schemas
├── analysis/
│   ├── engine.py           # Main orchestrator
│   ├── parsers/
│   │   ├── python_parser.py
│   │   ├── js_parser.py
│   │   └── java_parser.py
│   ├── detectors/
│   │   ├── security_detector.py
│   │   ├── performance_detector.py
│   │   ├── standards_detector.py
│   │   ├── test_coverage_detector.py
│   │   └── antipattern_detector.py
│   └── llm/
│       ├── prompt_builder.py    # Build LLM prompts
│       ├── inference.py         # Call Ministack
│       └── response_parser.py   # Parse LLM output
├── jira/
│   ├── client.py           # Jira REST API wrapper
│   ├── sync.py             # Sync issues to Jira
│   └── models.py           # Jira data models
├── db/
│   ├── models.py           # SQLAlchemy models
│   ├── cache.py            # Result caching
│   └── history.py          # Analysis history
├── config.py               # Configuration
└── requirements.txt        # Python dependencies
```

**Key Responsibilities**:
- Parse code files into AST
- Run pattern-based detectors
- Call LLM for AI-based analysis
- Aggregate and format results
- Cache results in SQLite
- Sync findings to Jira

### 3. Issue Detectors

#### Security Detector
- SQL injection patterns
- Hardcoded credentials
- Unsafe deserialization
- XSS vulnerabilities
- CSRF issues
- Weak cryptography

#### Performance Detector
- Inefficient loops (N² algorithms)
- Memory leaks (unclosed resources)
- Blocking operations
- Missing indexes/caching
- Large object creation in loops

#### Code Standards Detector
- Naming conventions (camelCase, snake_case)
- File/class size violations
- Cyclomatic complexity
- Unused variables/imports
- Line length violations
- Indentation consistency

#### Test Coverage Detector
- Missing unit tests
- Low test coverage %
- Missing edge case tests
- Mock/stub usage
- Test file naming conventions

#### Anti-Pattern Detector
- God objects/classes
- Magic numbers without constants
- Deep nesting
- Duplicate code
- Poor error handling
- Missing null checks

### 4. LLM Integration (Ministack)

**Setup**:
```bash
# Using Ollama (example)
ollama pull mistral  # or any suitable model
ollama serve         # Runs on localhost:11434
```

**Prompt Strategy**:
```
System: "You are a code review expert. Analyze the provided code snippet and identify issues."

User: """
[Code snippet]
[AST context]
[Previous findings]
"""

Response: """
{
  "issues": [
    {
      "type": "security|performance|standard|test|antipattern",
      "severity": "critical|high|medium|low",
      "line": 10,
      "message": "Clear explanation",
      "suggestion": "How to fix"
    }
  ]
}
"""
```

### 5. Jira Integration

**Setup**:
- Create new Jira board in local instance or cloud
- Configure REST API credentials
- Create custom fields: Code Line, File Path, Severity, Category

**Sync Flow**:
```
Analysis Results → Transform to Jira format → Create/Update Issues → Link to PR
```

**Issue Template**:
```
Title: [CATEGORY] Issue Type - Brief Description
Description:
- File: path/to/file.py
- Line: 42
- Severity: High
- Category: Security
- Message: Detailed issue description
- Suggestion: How to fix

Labels: [ai-review, security, high-priority]
```

## Data Flow

### 1. On-Demand Analysis (User Triggers)
```
User clicks "Analyze File" 
    ↓
VS Code Extension sends POST /analyze
    ↓
Backend receives code content
    ↓
Parsers extract AST and metadata
    ↓
Pattern detectors run (fast, rule-based)
    ↓
LLM service receives context + findings
    ↓
LLM provides AI-enhanced analysis
    ↓
Results aggregated and cached
    ↓
Response sent back to VS Code
    ↓
Extension displays issues inline
```

### 2. Watch Mode Analysis (Continuous)
```
File saved in VS Code
    ↓
Extension detects change
    ↓
Debounce (wait 1-2 seconds for more changes)
    ↓
Send to backend for analysis
    ↓
[Same as On-Demand from "Parsers extract AST"]
    ↓
Results displayed with minimal latency
```

### 3. Jira Sync
```
User clicks "Sync to Jira"
    ↓
Extension sends analysis results to backend
    ↓
Backend transforms issues to Jira format
    ↓
Jira REST API creates/updates issues
    ↓
Issues appear on Jira board
    ↓
User notified of sync completion
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **IDE** | VS Code Extension (TypeScript) | User interface |
| **Backend API** | Flask (Python) or Express (Node.js) | REST API server |
| **Code Analysis** | AST parsers, regex patterns | Code parsing |
| **LLM** | Ministack (Ollama, LocalAI) | AI inference |
| **Database** | SQLite | Caching & history |
| **External Integration** | Jira REST API | Issue tracking |
| **Containerization** | Docker Compose | Local deployment |

## Deployment - Docker Compose

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - OLLAMA_HOST=http://ollama:11434
      - JIRA_HOST=${JIRA_HOST}
      - JIRA_TOKEN=${JIRA_TOKEN}
    volumes:
      - ./backend:/app
      - ./db:/app/db

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama

  jira:  # Optional local Jira for testing
    image: atlassian/jira-software:latest
    ports:
      - "8080:8080"
    environment:
      - JIRA_DB_TYPE=h2

volumes:
  ollama-data:
```

## Performance Targets

- **Analysis Speed**: < 5 seconds per file (1000 LOC)
- **LLM Latency**: < 3 seconds per call
- **Extension Responsiveness**: < 100ms UI updates
- **Memory**: < 2GB backend, < 500MB extension
- **Caching**: 90% cache hit rate for repeated files

## Error Handling & Resilience

1. **LLM Unavailable**: Fall back to pattern-based detection
2. **Jira Offline**: Queue issues locally, sync when available
3. **Malformed Code**: Graceful parsing errors, report partial results
4. **Large Files**: Chunk analysis, stream results
5. **Network Issues**: Retry with exponential backoff

## Security Considerations

1. **No Data Transmission**: All analysis happens locally
2. **Credentials**: Store Jira token in VS Code secrets manager
3. **Code Privacy**: Never send code to external services
4. **Model Safety**: Use curated, open-source models only

## Next Steps

1. Set up local development environment
2. Implement basic backend API structure
3. Build pattern-based detectors first
4. Integrate Ministack/Ollama
5. Create VS Code extension scaffold
6. Implement Jira sync
7. Test with sample codebase
8. Iterate and improve detection quality
