"""
Naming Analyzer - Checks naming conventions and consistency.
"""

import re
from typing import List, Dict, Any
from collections import defaultdict
from healthpulse.analyzers import BaseAnalyzer
from healthpulse.scanner import FileInfo
from healthpulse.analyzers import RuleViolation


# Naming conventions per language
NAMING_CONVENTIONS = {
    'python': {
        'function': {'pattern': r'^[a-z_][a-z0-9_]*$', 'style': 'snake_case', 'regex': re.compile(r'def\s+(\w+)')},
        'class': {'pattern': r'^[A-Z][a-zA-Z0-9]*$', 'style': 'PascalCase', 'regex': re.compile(r'class\s+(\w+)')},
        'variable': {'pattern': r'^[a-z_][a-z0-9_]*$', 'style': 'snake_case', 'regex': re.compile(r'(\w+)\s*=')},
        'constant': {'pattern': r'^[A-Z_][A-Z0-9_]*$', 'style': 'UPPER_SNAKE_CASE', 'regex': re.compile(r'^([A-Z_][A-Z0-9_]*)\s*=')},
    },
    'javascript': {
        'function': {'pattern': r'^[a-z][a-zA-Z0-9]*$', 'style': 'camelCase', 'regex': re.compile(r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=)')},
        'class': {'pattern': r'^[A-Z][a-zA-Z0-9]*$', 'style': 'PascalCase', 'regex': re.compile(r'class\s+(\w+)')},
        'variable': {'pattern': r'^[a-z][a-zA-Z0-9]*$', 'style': 'camelCase', 'regex': re.compile(r'(?:const|let|var)\s+(\w+)\s*=')},
        'constant': {'pattern': r'^[A-Z_][A-Z0-9_]*$', 'style': 'UPPER_SNAKE_CASE', 'regex': re.compile(r'const\s+([A-Z_][A-Z0-9_]*)\s*=')},
    },
    'typescript': {
        'function': {'pattern': r'^[a-z][a-zA-Z0-9]*$', 'style': 'camelCase', 'regex': re.compile(r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=)')},
        'class': {'pattern': r'^[A-Z][a-zA-Z0-9]*$', 'style': 'PascalCase', 'regex': re.compile(r'(?:class|interface|type)\s+(\w+)')},
        'variable': {'pattern': r'^[a-z][a-zA-Z0-9]*$', 'style': 'camelCase', 'regex': re.compile(r'(?:const|let|var)\s+(\w+)\s*[:=]')},
        'constant': {'pattern': r'^[A-Z_][A-Z0-9_]*$', 'style': 'UPPER_SNAKE_CASE', 'regex': re.compile(r'const\s+([A-Z_][A-Z0-9_]*)\s*[:=]')},
    },
    'go': {
        'function': {'pattern': r'^[A-Z][a-zA-Z0-9]*$', 'style': 'PascalCase (exported) / camelCase (private)', 'regex': re.compile(r'func\s+(?:\([^)]+\)\s+)?(\w+)')},
        'variable': {'pattern': r'^[a-z][a-zA-Z0-9]*$', 'style': 'camelCase', 'regex': re.compile(r'(\w+)\s*:?=(?:[^=]|$)')},
    },
    'rust': {
        'function': {'pattern': r'^[a-z][a-zA-Z0-9_]*$', 'style': 'snake_case', 'regex': re.compile(r'fn\s+(\w+)')},
        'struct': {'pattern': r'^[A-Z][a-zA-Z0-9]*$', 'style': 'PascalCase', 'regex': re.compile(r'struct\s+(\w+)')},
        'enum': {'pattern': r'^[A-Z][a-zA-Z0-9]*$', 'style': 'PascalCase', 'regex': re.compile(r'enum\s+(\w+)')},
        'constant': {'pattern': r'^[A-Z_][A-Z0-9_]*$', 'style': 'UPPER_SNAKE_CASE', 'regex': re.compile(r'const\s+(\w+)')},
    },
    'java': {
        'class': {'pattern': r'^[A-Z][a-zA-Z0-9]*$', 'style': 'PascalCase', 'regex': re.compile(r'(?:class|interface|enum)\s+(\w+)')},
        'method': {'pattern': r'^[a-z][a-zA-Z0-9]*$', 'style': 'camelCase', 'regex': re.compile(r'(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+(\w+)\s*\(')},
        'constant': {'pattern': r'^[A-Z_][A-Z0-9_]*$', 'style': 'UPPER_SNAKE_CASE', 'regex': re.compile(r'static\s+final\s+\w+\s+([A-Z_][A-Z0-9_]*)')},
    },
}


class NamingAnalyzer(BaseAnalyzer):
    """Analyzes naming conventions."""

    def __init__(self):
        super().__init__()
        self.supported_languages = list(NAMING_CONVENTIONS.keys())
        self._naming_stats: Dict[str, Any] = {}

    def analyze(self, files: List[FileInfo]) -> List[RuleViolation]:
        """Analyze naming conventions."""
        violations = []
        stats = {
            'total_names_checked': 0,
            'convention_violations': 0,
            'inconsistent_names': 0,
            'poor_names': 0,
        }

        for file_info in files:
            lang_conventions = NAMING_CONVENTIONS.get(file_info.language)
            if not lang_conventions:
                continue

            file_violations, file_stats = self._analyze_file(file_info, lang_conventions)
            violations.extend(file_violations)
            stats['total_names_checked'] += file_stats['names_checked']
            stats['convention_violations'] += file_stats['violations']
            stats['inconsistent_names'] += file_stats['inconsistent']
            stats['poor_names'] += file_stats['poor_names']

        self._naming_stats = stats
        self._details = stats
        return violations

    def _analyze_file(self, file: FileInfo, conventions: dict) -> tuple:
        """Analyze a single file."""
        violations = []
        stats = {'names_checked': 0, 'violations': 0, 'inconsistent': 0, 'poor_names': 0}

        for entity_type, config in conventions.items():
            regex = config['regex']
            pattern = config['pattern']
            style = config['style']

            for i, line in enumerate(file.lines):
                stripped = line.strip()
                if not stripped or stripped.startswith('#') or stripped.startswith('//'):
                    continue

                match = regex.search(line)
                if match:
                    # Get the matched name (handle multiple groups)
                    name = None
                    for g in match.groups():
                        if g:
                            name = g
                            break
                    if name is None:
                        continue

                    stats['names_checked'] += 1

                    # Skip single-char names and dunder names
                    if len(name) <= 1 or (name.startswith('__') and name.endswith('__')):
                        continue

                    # Check convention
                    if not re.match(pattern, name):
                        stats['violations'] += 1
                        violations.append(self._add_violation(
                            'HP020', 'Naming Convention Violation', 'naming', 'info',
                            file.relative_path, i + 1,
                            f"'{name}' doesn't follow {style} convention for {entity_type}",
                            f"Rename to follow {style} style.",
                            stripped[:80]
                        ))

                    # Check for poor names
                    poor_patterns = {
                        'tmp': 'temporary', 'temp': 'temporary',
                        'data': 'generic', 'info': 'generic',
                        'obj': 'generic', 'item': 'generic',
                        'util': 'generic', 'helper': 'generic',
                        'mgr': 'abbreviation', 'mgr': 'abbreviation',
                    }
                    lower_name = name.lower()
                    if lower_name in poor_patterns:
                        stats['poor_names'] += 1
                        violations.append(self._add_violation(
                            'HP021', 'Poor Name Choice', 'naming', 'hint',
                            file.relative_path, i + 1,
                            f"'{name}' is a {poor_patterns[lower_name]} name, consider a more descriptive name",
                            "Use a name that clearly describes the purpose.",
                            stripped[:80]
                        ))

        return violations, stats

    def calculate_score(self, violations: List[RuleViolation],
                         files: List[FileInfo]) -> float:
        """Calculate naming score."""
        if not files:
            return 100.0

        total_lines = sum(f.line_count for f in files)
        if total_lines == 0:
            return 100.0

        deductions = 0
        for v in violations:
            if v.severity == 'warning':
                deductions += 4
            elif v.severity == 'info':
                deductions += 2
            else:
                deductions += 1

        factor = max(1, total_lines / 1000)
        return max(0, min(100, 100 - deductions / factor))
