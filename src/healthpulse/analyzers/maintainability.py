"""
Maintainability Analyzer - Assesses code maintainability metrics.
"""

import re
from typing import List, Dict, Any
from healthpulse.analyzers import BaseAnalyzer
from healthpulse.scanner import FileInfo
from healthpulse.analyzers import RuleViolation


class MaintainabilityAnalyzer(BaseAnalyzer):
    """Analyzes code maintainability."""

    def __init__(self):
        super().__init__()
        self.supported_languages = [
            'python', 'javascript', 'typescript', 'go', 'rust', 'java',
            'ruby', 'php', 'kotlin', 'swift', 'scala', 'shell', 'cpp', 'c',
        ]
        self._maint_stats: Dict[str, Any] = {}

    def analyze(self, files: List[FileInfo]) -> List[RuleViolation]:
        """Analyze code maintainability."""
        violations = []
        stats = {
            'total_files': len(files),
            'avg_line_length': 0,
            'long_lines': 0,
            'todo_count': 0,
            'fixme_count': 0,
            'hack_count': 0,
            'deprecated_count': 0,
            'dead_code_indicators': 0,
            'magic_numbers': 0,
        }

        total_chars = 0
        total_lines = 0

        for file_info in files:
            file_stats = {
                'long_lines': 0, 'todos': 0, 'fixmes': 0, 'hacks': 0,
                'deprecated': 0, 'dead_code': 0, 'magic_numbers': 0,
            }

            for i, line in enumerate(file_info.lines):
                stripped = line.strip()
                total_chars += len(line)
                total_lines += 1

                if not stripped:
                    continue

                # Long lines
                if len(line) > 120:
                    file_stats['long_lines'] += 1

                # TODO/FIXME/HACK markers
                if re.search(r'\bTODO\b', stripped, re.IGNORECASE):
                    file_stats['todos'] += 1
                if re.search(r'\bFIXME\b', stripped, re.IGNORECASE):
                    file_stats['fixmes'] += 1
                if re.search(r'\bHACK\b', stripped, re.IGNORECASE):
                    file_stats['hacks'] += 1
                if re.search(r'\bDEPRECATED\b', stripped, re.IGNORECASE):
                    file_stats['deprecated'] += 1

                # Dead code indicators
                if re.search(r'\bpass\s*$', stripped) and file_info.language == 'python':
                    # pass without context might indicate unfinished code
                    if i > 0 and not file_info.lines[i-1].strip().startswith('#'):
                        file_stats['dead_code'] += 1

                if re.search(r'\bnoqa\b', stripped, re.IGNORECASE):
                    file_stats['dead_code'] += 1

                if re.search(r'\bx\s*=\s*x\b', stripped):
                    file_stats['dead_code'] += 1

                # Magic numbers (numbers not 0, 1, -1, 2, 10, 100, etc.)
                if file_info.language == 'python':
                    magic_matches = re.findall(r'(?<![.\w])(?<!0x)\b([2-9]\d*|1[0-9]|1000+)\b', stripped)
                    for num in magic_matches:
                        if num not in ('2', '10', '100', '16', '32', '64', '256', '512', '1024'):
                            # Skip if it's part of a string, comment, or common pattern
                            if not stripped.startswith('#') and not stripped.startswith('//'):
                                file_stats['magic_numbers'] += 1
                                break  # Count once per line

            # Report long lines per file
            if file_stats['long_lines'] > 5:
                violations.append(self._add_violation(
                    'HP080', 'Excessive Long Lines', 'maintainability', 'info',
                    file_info.relative_path, 1,
                    f"File has {file_stats['long_lines']} lines exceeding 120 characters",
                    "Keep lines under 120 characters for readability.",
                    ""
                ))

            # Report TODO/FIXME
            if file_stats['todos'] > 0:
                for i, line in enumerate(file_info.lines):
                    if re.search(r'\bTODO\b', line, re.IGNORECASE):
                        stats['todo_count'] += 1
                        violations.append(self._add_violation(
                            'HP081', 'TODO Found', 'maintainability', 'hint',
                            file_info.relative_path, i + 1,
                            "TODO comment found - consider resolving it",
                            "Address the TODO or convert to an issue tracker item.",
                            line.strip()[:80]
                        ))

            if file_stats['fixmes'] > 0:
                for i, line in enumerate(file_info.lines):
                    if re.search(r'\bFIXME\b', line, re.IGNORECASE):
                        stats['fixme_count'] += 1
                        violations.append(self._add_violation(
                            'HP082', 'FIXME Found', 'maintainability', 'warning',
                            file_info.relative_path, i + 1,
                            "FIXME comment found - indicates known issue that needs fixing",
                            "Fix the issue and remove the FIXME comment.",
                            line.strip()[:80]
                        ))

            if file_stats['hacks'] > 0:
                for i, line in enumerate(file_info.lines):
                    if re.search(r'\bHACK\b', line, re.IGNORECASE):
                        stats['hack_count'] += 1
                        violations.append(self._add_violation(
                            'HP083', 'HACK Found', 'maintainability', 'warning',
                            file_info.relative_path, i + 1,
                            "HACK comment found - workaround code should be properly fixed",
                            "Replace the hack with a proper solution.",
                            line.strip()[:80]
                        ))

            if file_stats['deprecated'] > 0:
                stats['deprecated_count'] += file_stats['deprecated']

            stats['long_lines'] += file_stats['long_lines']
            stats['dead_code_indicators'] += file_stats['dead_code']
            stats['magic_numbers'] += file_stats['magic_numbers']

        if total_lines > 0:
            stats['avg_line_length'] = round(total_chars / total_lines, 1)

        self._maint_stats = stats
        self._details = stats
        return violations

    def calculate_score(self, violations: List[RuleViolation],
                         files: List[FileInfo]) -> float:
        """Calculate maintainability score."""
        if not files:
            return 100.0

        total_lines = sum(f.line_count for f in files)
        if total_lines == 0:
            return 100.0

        deductions = 0
        for v in violations:
            if v.severity == 'critical':
                deductions += 10
            elif v.severity == 'warning':
                deductions += 6
            elif v.severity == 'info':
                deductions += 3
            else:
                deductions += 1

        factor = max(1, total_lines / 1000)
        return max(0, min(100, 100 - deductions / factor))
