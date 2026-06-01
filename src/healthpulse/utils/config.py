"""
Configuration utility - Manages HealthPulse configuration.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


DEFAULT_CONFIG = {
    "version": "1.0",
    "language": "auto",
    "threshold": 60,
    "exclude": [
        "node_modules", ".git", "__pycache__", ".venv", "venv",
        "dist", "build", ".next", ".cache", "coverage",
    ],
    "rules": {
        "enabled": "all",
        "disabled": [],
    },
    "dimensions": {
        "complexity": {"weight": 1.0},
        "duplication": {"weight": 1.0},
        "naming": {"weight": 0.8},
        "security": {"weight": 1.2},
        "architecture": {"weight": 0.9},
        "documentation": {"weight": 0.7},
        "maintainability": {"weight": 1.0},
        "performance": {"weight": 0.8},
    },
    "ci": {
        "enabled": False,
        "threshold": 60,
    },
}

# Global config paths
GLOBAL_CONFIG_DIR = Path.home() / '.config' / 'healthpulse'
GLOBAL_CONFIG_FILE = GLOBAL_CONFIG_DIR / 'config.json'


class Config:
    """Manages HealthPulse configuration."""

    def __init__(self):
        self._config: Dict[str, Any] = {}

    def load(self) -> Dict[str, Any]:
        """Load configuration from file."""
        # Try local config first
        local_config = Path.cwd() / '.healthpulse.json'
        if local_config.exists():
            try:
                self._config = json.loads(local_config.read_text(encoding='utf-8'))
                return self._config
            except (json.JSONDecodeError, OSError):
                pass

        # Try global config
        if GLOBAL_CONFIG_FILE.exists():
            try:
                self._config = json.loads(GLOBAL_CONFIG_FILE.read_text(encoding='utf-8'))
                return self._config
            except (json.JSONDecodeError, OSError):
                pass

        # Use defaults
        self._config = DEFAULT_CONFIG.copy()
        return self._config

    def save(self) -> None:
        """Save configuration to file."""
        local_config = Path.cwd() / '.healthpulse.json'
        local_config.write_text(
            json.dumps(self._config, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    @property
    def exclude_patterns(self) -> str:
        """Get exclude patterns as comma-separated string."""
        excludes = self.get('exclude', [])
        return ','.join(excludes) if excludes else ''

    @property
    def threshold(self) -> int:
        """Get health score threshold."""
        return self.get('threshold', 60)

    @property
    def language(self) -> str:
        """Get default language setting."""
        return self.get('language', 'auto')
