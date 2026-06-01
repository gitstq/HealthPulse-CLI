"""
Complexity Analyzer - Measures code complexity metrics.
Cyclomatic complexity, nesting depth, function length, parameter count.
"""

import re
from typing import List, Dict, Any
from healthpulse.analyzers import BaseAnalyzer
from healthpulse.scanner import FileInfo
from healthpulse.analyzers import RuleViolation


class ComplexityAnalyzer(BaseAnalyzer):
    """Analyzes code complexity across multiple dimensions."""

    def __init__(self):
        super().__init__()
        self.supported_languages = [
            'python', 'javascript', 'typescript', 'go', 'rust', 'java',
            'ruby', 'php', 'kotlin', 'swift', 'scala', 'shell', 'cpp', 'c',
        ]
        self._complexity_data: Dict[str, Any] = {}

    def analyze(self, files: List[FileInfo]) -> List[RuleViolation]:
        """Analyze code complexity."""
        violations = []
        stats = {
            'total_functions': 0,
            'avg_complexity': 0,
            'max_complexity': 0,
            'deep_nesting_count': 0,
            'long_function_count': 0,
            'many_params_count': 0,
        }
        total_complexity = 0

        for file_info in files:
            file_violations, file_stats = self._analyze_file(file_info)
            violations.extend(file_violations)
            stats['total_functions'] += file_stats['function_count']
            total_complexity += file_stats['total_complexity']
            stats['max_complexity'] = max(stats['max_complexity'], file_stats['max_complexity'])
            stats['deep_nesting_count'] += file_stats['deep_nesting']
            stats['long_function_count'] += file_stats['long_functions']
            stats['many_params_count'] += file_stats['many_params']

        if stats['total_functions'] > 0:
            stats['avg_complexity'] = round(total_complexity / stats['total_functions'], 1)

        self._complexity_data = stats
        self._details = stats
        return violations

    def _analyze_file(self, file: FileInfo) -> tuple:
        """Analyze a single file for complexity issues."""
        violations = []
        stats = {
            'function_count': 0,
            'total_complexity': 0,
            'max_complexity': 0,
            'deep_nesting': 0,
            'long_functions': 0,
            'many_params': 0,
        }

        if file.language == 'python':
            violations, stats = self._analyze_python(file)
        elif file.language in ('javascript', 'typescript'):
            violations, stats = self._analyze_js(file)
        elif file.language == 'go':
            violations, stats = self._analyze_go(file)
        elif file.language == 'rust':
            violations, stats = self._analyze_rust(file)
        elif file.language == 'java':
            violations, stats = self._analyze_java(file)
        else:
            violations, stats = self._analyze_generic(file)

        return violations, stats

    def _analyze_python(self, file: FileInfo) -> tuple:
        """Analyze Python complexity."""
        violations = []
        stats = {
            'function_count': 0, 'total_complexity': 0,
            'max_complexity': 0, 'deep_nesting': 0,
            'long_functions': 0, 'many_params': 0,
        }

        func_pattern = re.compile(r'^(\s*)def\s+(\w+)\s*\(([^)]*)\)')
        class_pattern = re.compile(r'^(\s*)class\s+(\w+)')
        nesting_keywords = {'if', 'elif', 'else', 'for', 'while', 'try', 'except', 'with'}

        current_indent = 0
        func_start = 0
        func_lines = 0
        func_complexity = 1
        in_function = False
        func_name = ""
        func_params = ""
        func_base_indent = 0

        for i, line in enumerate(file.lines):
            stripped = line.strip()

            # Skip empty lines and comments
            if not stripped or stripped.startswith('#'):
                continue

            # Calculate indent level
            indent = len(line) - len(line.lstrip())

            # Detect function definition
            func_match = func_pattern.match(line)
            if func_match:
                if in_function and func_lines > 0:
                    stats = self._check_function(
                        file, func_start, func_name, func_params,
                        func_lines, func_complexity, func_base_indent,
                        violations, stats
                    )

                in_function = True
                func_start = i
                func_name = func_match.group(2)
                func_params = func_match.group(3)
                func_lines = 0
                func_complexity = 1
                func_base_indent = indent
                stats['function_count'] += 1
                continue

            # Detect class definition (reset function context)
            class_match = class_pattern.match(line)
            if class_match and in_function:
                stats = self._check_function(
                    file, func_start, func_name, func_params,
                    func_lines, func_complexity, func_base_indent,
                    violations, stats
                )
                in_function = False

            if in_function and indent > func_base_indent:
                func_lines += 1

                # Count branching complexity
                first_word = stripped.split()[0] if stripped.split() else ''
                if first_word in nesting_keywords:
                    func_complexity += 1

                # Check nesting depth
                relative_indent = indent - func_base_indent
                if relative_indent > 24:  # > 6 levels of 4-space indent
                    stats['deep_nesting'] += 1
                    violations.append(self._add_violation(
                        'HP001', 'Deep Nesting', 'complexity', 'warning',
                        file.relative_path, i + 1,
                        f"Deep nesting detected in '{func_name}' (level {relative_indent // 4})",
                        "Consider extracting nested logic into helper functions.",
                        stripped
                    ))

        # Check last function
        if in_function and func_lines > 0:
            stats = self._check_function(
                file, func_start, func_name, func_params,
                func_lines, func_complexity, func_base_indent,
                violations, stats
            )

        return violations, stats

    def _analyze_js(self, file: FileInfo) -> tuple:
        """Analyze JavaScript/TypeScript complexity."""
        violations = []
        stats = {
            'function_count': 0, 'total_complexity': 0,
            'max_complexity': 0, 'deep_nesting': 0,
            'long_functions': 0, 'many_params': 0,
        }

        func_pattern = re.compile(
            r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:\([^)]*\)|[^=])\s*=>|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?function)'
        )
        nesting_keywords = {'if', 'else', 'for', 'while', 'switch', 'case', 'try', 'catch'}

        in_function = False
        func_start = 0
        func_lines = 0
        func_complexity = 1
        func_name = ""
        brace_depth = 0
        func_brace_start = 0

        for i, line in enumerate(file.lines):
            stripped = line.strip()
            if not stripped or stripped.startswith('//') or stripped.startswith('*'):
                continue

            func_match = func_pattern.search(line)
            if func_match:
                if in_function and func_lines > 0:
                    stats = self._check_function(
                        file, func_start, func_name, "",
                        func_lines, func_complexity, 0,
                        violations, stats
                    )
                in_function = True
                func_start = i
                func_name = func_match.group(1) or func_match.group(2) or func_match.group(3) or 'anonymous'
                func_lines = 0
                func_complexity = 1
                stats['function_count'] += 1

            if in_function:
                func_lines += 1
                open_braces = stripped.count('{')
                close_braces = stripped.count('}')
                brace_depth += open_braces - close_braces

                if open_braces > 0 and func_brace_start == 0:
                    func_brace_start = brace_depth

                first_word = stripped.split()[0] if stripped.split() else ''
                if first_word in nesting_keywords:
                    func_complexity += 1

                if brace_depth <= func_brace_start and close_braces > 0:
                    stats = self._check_function(
                        file, func_start, func_name, "",
                        func_lines, func_complexity, 0,
                        violations, stats
                    )
                    in_function = False
                    func_brace_start = 0

        return violations, stats

    def _analyze_go(self, file: FileInfo) -> tuple:
        """Analyze Go complexity."""
        violations = []
        stats = {
            'function_count': 0, 'total_complexity': 0,
            'max_complexity': 0, 'deep_nesting': 0,
            'long_functions': 0, 'many_params': 0,
        }

        func_pattern = re.compile(r'func\s+(?:\([^)]+\)\s+)?(\w+)\s*\(([^)]*)\)')
        nesting_keywords = {'if', 'else', 'for', 'range', 'switch', 'case', 'select', 'go', 'defer'}

        in_function = False
        func_start = 0
        func_lines = 0
        func_complexity = 1
        func_name = ""

        for i, line in enumerate(file.lines):
            stripped = line.strip()
            if not stripped or stripped.startswith('//'):
                continue

            func_match = func_pattern.match(line)
            if func_match:
                if in_function:
                    stats = self._check_function(
                        file, func_start, func_name, func_match.group(2),
                        func_lines, func_complexity, 0,
                        violations, stats
                    )
                in_function = True
                func_start = i
                func_name = func_match.group(1)
                func_lines = 0
                func_complexity = 1
                stats['function_count'] += 1
                continue

            if in_function:
                if stripped == '}':
                    stats = self._check_function(
                        file, func_start, func_name, "",
                        func_lines, func_complexity, 0,
                        violations, stats
                    )
                    in_function = False
                else:
                    func_lines += 1
                    first_word = stripped.split()[0] if stripped.split() else ''
                    if first_word in nesting_keywords:
                        func_complexity += 1

        return violations, stats

    def _analyze_rust(self, file: FileInfo) -> tuple:
        """Analyze Rust complexity."""
        violations = []
        stats = {
            'function_count': 0, 'total_complexity': 0,
            'max_complexity': 0, 'deep_nesting': 0,
            'long_functions': 0, 'many_params': 0,
        }

        func_pattern = re.compile(r'(?:pub\s+)?(?:async\s+)?fn\s+(\w+)\s*\(([^)]*)\)')
        nesting_keywords = {'if', 'else', 'for', 'while', 'loop', 'match', 'if let', 'while let'}

        in_function = False
        func_start = 0
        func_lines = 0
        func_complexity = 1
        func_name = ""

        for i, line in enumerate(file.lines):
            stripped = line.strip()
            if not stripped or stripped.startswith('//'):
                continue

            func_match = func_pattern.match(line)
            if func_match:
                if in_function:
                    stats = self._check_function(
                        file, func_start, func_name, func_match.group(2),
                        func_lines, func_complexity, 0,
                        violations, stats
                    )
                in_function = True
                func_start = i
                func_name = func_match.group(1)
                func_lines = 0
                func_complexity = 1
                stats['function_count'] += 1
                continue

            if in_function:
                if stripped.startswith('}'):
                    stats = self._check_function(
                        file, func_start, func_name, "",
                        func_lines, func_complexity, 0,
                        violations, stats
                    )
                    in_function = False
                else:
                    func_lines += 1
                    first_word = stripped.split()[0] if stripped.split() else ''
                    if first_word in nesting_keywords:
                        func_complexity += 1

        return violations, stats

    def _analyze_java(self, file: FileInfo) -> tuple:
        """Analyze Java complexity."""
        violations = []
        stats = {
            'function_count': 0, 'total_complexity': 0,
            'max_complexity': 0, 'deep_nesting': 0,
            'long_functions': 0, 'many_params': 0,
        }

        func_pattern = re.compile(
            r'(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+(\w+)\s*\(([^)]*)\)\s*(?:throws\s+[\w,\s]+)?\s*\{?'
        )
        nesting_keywords = {'if', 'else', 'for', 'while', 'switch', 'case', 'try', 'catch'}

        in_function = False
        func_start = 0
        func_lines = 0
        func_complexity = 1
        func_name = ""

        for i, line in enumerate(file.lines):
            stripped = line.strip()
            if not stripped or stripped.startswith('//') or stripped.startswith('*'):
                continue

            func_match = func_pattern.match(line)
            if func_match:
                if in_function:
                    stats = self._check_function(
                        file, func_start, func_name, func_match.group(2),
                        func_lines, func_complexity, 0,
                        violations, stats
                    )
                in_function = True
                func_start = i
                func_name = func_match.group(1)
                func_lines = 0
                func_complexity = 1
                stats['function_count'] += 1
                continue

            if in_function:
                if stripped == '}':
                    stats = self._check_function(
                        file, func_start, func_name, "",
                        func_lines, func_complexity, 0,
                        violations, stats
                    )
                    in_function = False
                else:
                    func_lines += 1
                    first_word = stripped.split()[0] if stripped.split() else ''
                    if first_word in nesting_keywords:
                        func_complexity += 1

        return violations, stats

    def _analyze_generic(self, file: FileInfo) -> tuple:
        """Generic complexity analysis for unsupported languages."""
        violations = []
        stats = {
            'function_count': 0, 'total_complexity': 0,
            'max_complexity': 0, 'deep_nesting': 0,
            'long_functions': 0, 'many_params': 0,
        }

        # Basic line-length analysis
        for i, line in enumerate(file.lines):
            if len(line) > 150:
                violations.append(self._add_violation(
                    'HP008', 'Long Line', 'complexity', 'info',
                    file.relative_path, i + 1,
                    f"Line is {len(line)} characters long (recommended: < 120)",
                    "Consider breaking long lines into multiple statements.",
                    line.strip()[:80]
                ))

        return violations, stats

    def _check_function(self, file, start, name, params, lines, complexity, base_indent, violations, stats):
        """Check a single function for complexity issues."""
        stats['total_complexity'] += complexity
        stats['max_complexity'] = max(stats['max_complexity'], complexity)

        # High cyclomatic complexity
        if complexity > 10:
            stats['deep_nesting'] += 1
            violations.append(self._add_violation(
                'HP002', 'High Cyclomatic Complexity', 'complexity', 'warning',
                file.relative_path, start + 1,
                f"Function '{name}' has cyclomatic complexity of {complexity} (recommended: <= 10)",
                "Break down complex functions into smaller, focused helper functions.",
                self._get_line(file, start)
            ))

        # Long function
        if lines > 50:
            stats['long_functions'] += 1
            violations.append(self._add_violation(
                'HP003', 'Long Function', 'complexity', 'warning',
                file.relative_path, start + 1,
                f"Function '{name}' is {lines} lines long (recommended: <= 50)",
                "Extract logical blocks into separate functions.",
                self._get_line(file, start)
            ))

        # Many parameters
        if params:
            param_count = len([p.strip() for p in params.split(',') if p.strip()])
            if param_count > 5:
                stats['many_params'] += 1
                violations.append(self._add_violation(
                    'HP004', 'Too Many Parameters', 'complexity', 'info',
                    file.relative_path, start + 1,
                    f"Function '{name}' has {param_count} parameters (recommended: <= 5)",
                    "Consider using a data class or options object to group related parameters.",
                    self._get_line(file, start)
                ))

        return stats

    def calculate_score(self, violations: List[RuleViolation],
                         files: List[FileInfo]) -> float:
        """Calculate complexity score."""
        if not files:
            return 100.0

        total_lines = sum(f.line_count for f in files)
        if total_lines == 0:
            return 100.0

        # Deduct points for violations
        deductions = 0
        for v in violations:
            if v.severity == 'critical':
                deductions += 8
            elif v.severity == 'warning':
                deductions += 5
            elif v.severity == 'info':
                deductions += 2
            else:
                deductions += 1

        # Normalize by code size (per 1000 lines)
        factor = max(1, total_lines / 1000)
        normalized_deductions = deductions / factor

        return max(0, min(100, 100 - normalized_deductions))
