"""Configuration loader and manager"""
import os
from typing import Dict, Type, Optional
from .base import CodebaseConfigTemplate
from .python import PythonCodebaseConfig
from .terraform import TerraformCodebaseConfig
from .typescript import TypeScriptCodebaseConfig

class ConfigManager:
    """Manages codebase configuration selection and loading"""
    
    # Register all available configurations
    AVAILABLE_CONFIGS: Dict[str, Type[CodebaseConfigTemplate]] = {
        'python': PythonCodebaseConfig,
        'terraform': TerraformCodebaseConfig,
        'typescript': TypeScriptCodebaseConfig,
        'ts': TypeScriptCodebaseConfig,  # Alias
        'js': TypeScriptCodebaseConfig,  # Alias
    }
    
    @classmethod
    def get_config(cls, config_name: Optional[str] = None) -> CodebaseConfigTemplate:
        """
        Get configuration by name or from environment
        
        Args:
            config_name: Name of config (python, terraform, typescript)
                        If None, uses CODEBASE_STYLE env var or defaults to generic
        
        Returns:
            CodebaseConfigTemplate instance
        """
        if config_name is None:
            config_name = os.getenv('CODEBASE_STYLE', 'python').lower()
        
        config_class = cls.AVAILABLE_CONFIGS.get(config_name)
        if config_class is None:
            # Fallback to base template
            from .base import CodebaseConfigTemplate
            return CodebaseConfigTemplate()
        
        return config_class()
    
    @classmethod
    def list_configs(cls) -> Dict[str, str]:
        """List all available configurations"""
        return {
            name: config_class.DESCRIPTION
            for name, config_class in cls.AVAILABLE_CONFIGS.items()
        }
    
    @classmethod
    def register_config(cls, name: str, config_class: Type[CodebaseConfigTemplate]):
        """Register a custom configuration"""
        cls.AVAILABLE_CONFIGS[name.lower()] = config_class
    
    @classmethod
    def auto_detect(cls, root_path: str = '.') -> CodebaseConfigTemplate:
        """
        Auto-detect codebase type based on files present
        
        Args:
            root_path: Root directory to check
        
        Returns:
            Best matching configuration
        """
        import os
        
        # Check for files that indicate codebase type
        indicators = {
            'python': [
                'requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile',
                'manage.py', 'wsgi.py',  # Django/Flask
            ],
            'terraform': [
                '*.tf', 'terraform.tfvars', '.terraform/',
                'Dockerfile', 'docker-compose.yml',
                'k8s/', 'helm/', '.gitlab-ci.yml',
            ],
            'typescript': [
                'tsconfig.json', 'package.json', 'yarn.lock', 'pnpm-lock.yaml',
                'next.config.js', '.eslintrc', '.prettierrc',
            ],
        }
        
        found_indicators = {config: 0 for config in indicators}
        
        # Walk directory and count indicators
        for root, dirs, files in os.walk(root_path):
            # Skip hidden and common non-source directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            dirs[:] = [d for d in dirs if d not in ['node_modules', 'venv', '.venv']]
            
            for file in files:
                for config, patterns in indicators.items():
                    for pattern in patterns:
                        if pattern.startswith('*.'):
                            # File extension pattern
                            if file.endswith(pattern[1:]):
                                found_indicators[config] += 1
                        elif file == pattern:
                            found_indicators[config] += 2  # Higher weight for exact match
        
        # Return config with most indicators
        best_config = max(found_indicators, key=found_indicators.get)
        if found_indicators[best_config] > 0:
            return cls.get_config(best_config)
        
        # Default to Python if nothing detected
        return cls.get_config('python')
