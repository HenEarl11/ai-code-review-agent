"""Terraform/Infrastructure as Code configuration"""
from .base import CodebaseConfigTemplate, Severity
from typing import List, Dict

class TerraformCodebaseConfig(CodebaseConfigTemplate):
    """Configuration optimized for Terraform, Kubernetes, and IaC codebases"""
    
    NAME = "terraform"
    DESCRIPTION = "Configuration for Terraform, Kubernetes YAML, Docker, and Infrastructure as Code"
    SUPPORTED_LANGUAGES = ["terraform", "hcl", "yaml", "dockerfile"]
    
    # Use general model for IaC analysis
    LLM_MODEL = "mistral"
    LLM_TEMPERATURE = 0.2
    
    # Infrastructure-specific detectors
    ACTIVE_DETECTORS = [
        "security",
        "terraform_best_practices",
        "kubernetes_best_practices",
        "docker_best_practices",
        "performance",
        "cost_optimization",
        "standards",
    ]
    
    # Analyze infrastructure files
    ANALYZE_PATTERNS = [
        "**/*.tf",
        "**/*.tfvars",
        "**/k8s/**/*.yaml",
        "**/k8s/**/*.yml",
        "**/helm/**/*.yaml",
        "**/helm/**/*.yml",
        "**/docker-compose*.yml",
        "**/docker-compose*.yaml",
        "**/Dockerfile",
        "**/.github/workflows/*.yml",
        "**/.github/workflows/*.yaml",
        "**/.gitlab-ci.yml",
    ]
    
    # IaC-specific ignore patterns
    IGNORE_PATTERNS = [
        "**/terraform.tfstate*",
        "**/.terraform/**",
        "**/.terraform.lock.hcl",
        "**/node_modules/**",
        "**/__pycache__/**",
    ]
    
    # Override severities for infrastructure
    SEVERITY_OVERRIDES = {
        "missing_resource_limits": Severity.CRITICAL,
        "hardcoded_credentials": Severity.CRITICAL,
        "public_storage_bucket": Severity.CRITICAL,
        "single_replica_production": Severity.HIGH,
        "missing_network_policy": Severity.HIGH,
        "unencrypted_database": Severity.CRITICAL,
        "missing_backup_policy": Severity.HIGH,
        "no_auto_scaling": Severity.MEDIUM,
        "missing_resource_tags": Severity.LOW,
        "inconsistent_naming": Severity.LOW,
    }
    
    # Infrastructure-specific LLM prompt
    LLM_SYSTEM_PROMPT = """You are an expert Infrastructure as Code (IaC) and DevOps reviewer.

ANALYZE for:

1. SECURITY ISSUES (CRITICAL):
   - Hardcoded secrets, API keys, credentials
   - Public S3 buckets or storage access
   - Unencrypted databases (RDS, MongoDB, etc)
   - Missing network security groups/policies
   - Overly permissive IAM roles
   - Unencrypted data in transit
   - Missing TLS/SSL certificates
   - Exposed SSH ports to 0.0.0.0

2. KUBERNETES BEST PRACTICES:
   - Missing resource requests/limits (CPU/Memory)
   - Single replica in production (no HA)
   - Missing health checks (liveness/readiness probes)
   - Missing network policies
   - Containers running as root
   - Latest tag instead of specific versions
   - Missing resource quotas
   - No pod security policies
   - Missing persistent volume backups

3. TERRAFORM BEST PRACTICES:
   - Hardcoded values instead of variables
   - Missing lifecycle rules
   - Inefficient resource dependencies
   - Missing count/for_each for repetition
   - No remote backend configuration
   - Missing variable validation
   - Lack of comments/documentation
   - Unused variables or outputs

4. DOCKER BEST PRACTICES:
   - Using latest base image tag
   - Running as root user
   - Large image sizes
   - Missing HEALTHCHECK
   - Unnecessary layers
   - Not using .dockerignore
   - Secrets in build args

5. CI/CD PIPELINE:
   - Missing tests in pipeline
   - No staging environment validation
   - Manual approval steps missing for prod
   - Secrets exposed in logs
   - No rollback strategy
   - Missing deployment notifications

6. COST OPTIMIZATION:
   - Oversized compute resources
   - No auto-scaling configured
   - Unused resources
   - No spot instances considered
   - Reserved capacity not optimized

7. PERFORMANCE & RELIABILITY:
   - Single point of failure
   - Missing redundancy
   - No load balancing
   - Missing caching layer
   - No rate limiting
   - Inefficient database queries

Return ONLY valid JSON array with: line, severity, type, message, suggestion."""
    
    # Infrastructure-specific settings
    REQUIRE_HA_PRODUCTION = True  # Require high availability in prod
    REQUIRE_ENCRYPTION = True      # Require encryption at rest
    REQUIRE_BACKUPS = True          # Require backup policies
    REQUIRE_MONITORING = True       # Require monitoring/alerting
    REQUIRE_NETWORK_POLICIES = True # Require network segmentation
    MIN_REPLICA_PRODUCTION = 3      # Minimum replicas in prod
    REQUIRE_RESOURCE_LIMITS = True  # Require K8s resource limits
    ALLOWED_BASE_IMAGES = [         # Restrict base images
        "ubuntu:20.04",
        "ubuntu:22.04",
        "debian:11",
        "debian:12",
        "alpine:3.16",
        "alpine:3.17",
        "python:3.11-slim",
        "python:3.10-slim",
        "node:18-alpine",
        "node:20-alpine",
    ]
    
    # Cloud provider detection
    CLOUD_PROVIDERS = {
        "aws": ["aws", "aws_", "AWS", "provider = \"aws\""],
        "gcp": ["google", "gcp", "GCP", "provider = \"google\""],
        "azure": ["azure", "azurerm", "AZURE", "provider = \"azurerm\""],
        "digitalocean": ["digitalocean", "do_"],
    }
    
    # Provider-specific checks
    PROVIDER_CHECKS = {
        "aws": [
            "aws_security_group_rules",
            "aws_s3_bucket_policies",
            "aws_iam_roles",
            "aws_rds_encryption",
            "aws_vpc_flow_logs",
        ],
        "gcp": [
            "gcp_firewall_rules",
            "gcp_iam_bindings",
            "gcp_storage_bucket_acl",
            "gcp_cloud_sql_encryption",
        ],
        "azure": [
            "azure_network_security_groups",
            "azure_storage_account_encryption",
            "azure_sql_database_encryption",
        ],
    }
    
    @classmethod
    def to_dict(cls) -> Dict:
        config = super().to_dict()
        config.update({
            "require_ha_production": cls.REQUIRE_HA_PRODUCTION,
            "require_encryption": cls.REQUIRE_ENCRYPTION,
            "require_backups": cls.REQUIRE_BACKUPS,
            "min_replica_production": cls.MIN_REPLICA_PRODUCTION,
            "require_resource_limits": cls.REQUIRE_RESOURCE_LIMITS,
        })
        return config
