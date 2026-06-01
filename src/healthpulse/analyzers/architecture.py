"""
Architecture Analyzer - Checks code architecture, module structure, and design patterns.
"""

import re
import os
from typing import List, Dict, Any
from collections import defaultdict
from healthpulse.analyzers import BaseAnalyzer
from healthpulse.scanner import FileInfo
from healthpulse.analyzers import RuleViolation


class ArchitectureAnalyzer(BaseAnalyzer):
    """Analyzes code architecture and structure."""

    def __init__(self):
        super().__init__()
        self.supported_languages = [
            'python', 'javascript', 'typescript', 'go', 'rust', 'java',
            'ruby', 'php', 'kotlin', 'swift', 'scala', 'shell', 'cpp', 'c',
        ]
        self._arch_stats: Dict[str, Any] = {}

    def analyze(self, files: List[FileInfo]) -> List[RuleViolation]:
        """Analyze code architecture."""
        violations = []
        stats = {
            'total_files': len(files),
            'avg_file_length': 0,
            'large_files': 0,
            'god_classes': 0,
            'circular_import_risk': 0,
            'missing_init': 0,
            'flat_structure': 0,
        }

        if not files:
            self._arch_stats = stats
            self._details = stats
            return violations

        total_lines = sum(f.line_count for f in files)
        stats['avg_file_length'] = round(total_lines / len(files), 1) if files else 0

        # Check file sizes
        for file_info in files:
            if file_info.line_count > 500:
                stats['large_files'] += 1
                violations.append(self._add_violation(
                    'HP060', 'Large File', 'architecture', 'warning',
                    file_info.relative_path, 1,
                    f"File has {file_info.line_count} lines (recommended: <= 500)",
                    "Split into smaller, focused modules.",
                    ""
                ))

        # Check for god classes (Python)
        python_files = [f for f in files if f.language == 'python']
        for file_info in python_files:
            class_count = 0
            method_count = 0
            for line in file_info.lines:
                if re.match(r'^\s*class\s+\w+', line):
                    class_count += 1
                if re.match(r'^\s*def\s+\w+', line):
                    method_count += 1

            if class_count == 1 and method_count > 20:
                stats['god_classes'] += 1
                violations.append(self._add_violation(
                    'HP061', 'God Class', 'architecture', 'warning',
                    file_info.relative_path, 1,
                    f"Single file with {method_count} methods may be a God Class",
                    "Split into smaller, single-responsibility classes.",
                    ""
                ))

        # Check directory structure
        dir_structure = defaultdict(int)
        for file_info in files:
            parts = file_info.path.parts
            if len(parts) > 1:
                dir_structure[str(parts[-2])] += 1

        # Check for flat structure (all files in root)
        root_files = sum(1 for f in files if len(f.path.parts) == 1)
        if root_files > 10 and len(files) > 15:
            stats['flat_structure'] += 1
            violations.append(self._add_violation(
                'HP062', 'Flat Directory Structure', 'architecture', 'info',
                '.', 1,
                f"{root_files} files in root directory, consider organizing into subdirectories",
                "Group related files into logical directories/packages.",
                ""
            ))

        # Check for missing __init__.py in Python packages
        if python_files:
            dirs_with_py = set()
            for f in python_files:
                if len(f.path.parts) > 1:
                    dirs_with_py.add(str(f.path.parent))

            for dir_path in dirs_with_py:
                init_path = os.path.join(dir_path, '__init__.py')
                has_init = any(str(f.path) == init_path for f in python_files)
                if not has_init:
                    stats['missing_init'] += 1
                    violations.append(self._add_violation(
                        'HP063', 'Missing __init__.py', 'architecture', 'info',
                        dir_path, 1,
                        f"Python package directory '{dir_path}' is missing __init__.py",
                        "Add __init__.py to make it a proper Python package.",
                        ""
                    ))

        # Check for circular import risks (simplified)
        import_map = defaultdict(list)
        for file_info in files:
            if file_info.language == 'python':
                for i, line in enumerate(file_info.lines):
                    match = re.match(r'^\s*(?:from|import)\s+([\w.]+)', line)
                    if match:
                        module = match.group(1).split('.')[0]
                        import_map[module].append(file_info.path.stem)

        # Check for tight coupling (many files importing same module)
        for module, importers in import_map.items():
            if len(importers) > len(files) * 0.5 and len(importers) > 5:
                violations.append(self._add_violation(
                    'HP064', 'High Coupling', 'architecture', 'info',
                    '.', 1,
                    f"Module '{module}' is imported by {len(importers)} files ({round(len(importers)/len(files)*100)}%)",
                    "Consider introducing an abstraction layer to reduce coupling.",
                    ""
                ))
                break  # Only report once

        self._arch_stats = stats
        self._details = stats
        return violations

    def calculate_score(self, violations: List[RuleViolation],
                         files: List[FileInfo]) -> float:
        """Calculate architecture score."""
        if not files:
            return 100.0

        deductions = 0
        for v in violations:
            if v.severity == 'warning':
                deductions += 6
            elif v.severity == 'info':
                deductions += 3
            else:
                deductions += 1

        factor = max(1, len(files) / 10)
        return max(0, min(100, 100 - deductions / factor))
