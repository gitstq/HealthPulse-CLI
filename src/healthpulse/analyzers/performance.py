"""
Performance Analyzer - Detects potential performance issues and anti-patterns.
"""

import re
from typing import List, Dict, Any
from healthpulse.analyzers import BaseAnalyzer
from healthpulse.scanner import FileInfo
from healthpulse.analyzers import RuleViolation


PERFORMANCE_PATTERNS = {
    'python': [
        (r'\+\s*["\']', 'HP090', 'String Concatenation in Loop', 'info',
         'String concatenation with + in loop is inefficient',
         'Use "".join() or f-strings for better performance'),
        (r'for\s+\w+\s+in\s+range\s*\(\s*len\s*\(', 'HP091', 'Range-based Index Iteration', 'info',
         'Using range(len()) instead of direct iteration',
         'Iterate directly: for item in collection:'),
        (r'import\s+\*', 'HP092', 'Wildcard Import', 'info',
         'Wildcard imports can slow startup and cause namespace pollution',
         'Import only the specific names you need'),
        (r'global\s+\w+', 'HP093', 'Global Variable Usage', 'info',
         'Excessive global variable usage can impact performance and maintainability',
         'Use function arguments or class attributes instead'),
        (r'\.append\s*\([^)]*\.append', 'HP094', 'Nested Append in Loop', 'info',
         'Nested list operations in loops may indicate O(n²) complexity',
         'Consider using list comprehension or itertools'),
        (r'time\.sleep\s*\(\s*\d+\s*\)', 'HP095', 'Hardcoded Sleep', 'warning',
         'Hardcoded sleep duration may cause unnecessary delays',
         'Use configurable delays or event-driven patterns'),
        (r'os\.path\.join\s*\(', 'HP096', 'Path Operation in Loop', 'info',
         'Repeated path operations in a loop may be inefficient',
         'Pre-compute paths outside the loop when possible'),
        (r'open\s*\([^)]*\)\s*;', 'HP097', 'File Not Properly Closed', 'warning',
         'File opened without context manager may leak file handles',
         'Use "with open() as f:" pattern'),
    ],
    'javascript': [
        (r'for\s*\([^)]*\.length\s*;', 'HP098', 'Array Length in Loop Condition', 'info',
         'Accessing .length in each iteration is slightly slower',
         'Cache the length: for (let i = 0, len = arr.length; i < len; i++)'),
        (r'var\s+\w+', 'HP099', 'Var Declaration', 'info',
         'var has function scope and hoisting issues',
         'Use const or let for block-scoped variables'),
        (r'console\.log\s*\(', 'HP100', 'Console Log in Production', 'info',
         'Console.log statements should be removed in production',
         'Use a proper logging library and remove debug logs'),
        (r'document\.querySelector\s*\([^)]*\)\s*;', 'HP101', 'Repeated DOM Query', 'info',
         'DOM queries are expensive, cache the result',
         'Store query result in a variable and reuse it'),
        (r'\+\s*["\']', 'HP090', 'String Concatenation', 'info',
         'String concatenation with + may be inefficient',
         'Use template literals: `string ${variable}`'),
        (r'setTimeout\s*\(\s*function', 'HP102', 'setTimeout with Function', 'hint',
         'setTimeout with function reference is slightly slower',
         'Use arrow function or named function reference'),
    ],
    'typescript': [
        (r'console\.log\s*\(', 'HP100', 'Console Log in Production', 'info',
         'Console.log statements should be removed in production',
         'Use a proper logging library'),
        (r'as\s+any', 'HP103', 'Type Assertion to Any', 'warning',
         'Casting to any defeats TypeScript type safety',
         'Use proper types or unknown with type guards'),
        (r'!\.', 'HP104', 'Non-null Assertion', 'info',
         'Non-null assertion bypasses null checks',
         'Use optional chaining (?.) or proper null handling'),
    ],
    'go': [
        (r'var\s+\w+', 'HP105', 'Var Declaration', 'hint',
         'var is rarely needed in Go, prefer :=',
         'Use short variable declaration := when possible'),
        (r'fmt\.Sprintf\s*\([^)]*\)\s*,', 'HP106', 'Unnecessary String Formatting', 'info',
         'fmt.Sprintf for simple conversions is slower',
         'Use strconv or direct conversion for simple types'),
    ],
    'rust': [
        (r'\.clone\s*\(\)', 'HP107', 'Excessive Cloning', 'info',
         'Clone operations can be expensive',
         'Use references (&) or move semantics when possible'),
        (r'\.unwrap\s*\(\)', 'HP108', 'Unchecked Unwrap', 'warning',
         'unwrap() will panic on None/Err',
         'Use pattern matching or expect() with a message'),
        (r'unsafe\s*\{', 'HP052', 'Unsafe Block', 'warning',
         'Unsafe code bypasses Rust safety guarantees',
         'Minimize unsafe blocks and document safety invariants'),
    ],
    'java': [
        (r'new\s+String\s*\(', 'HP109', 'Unnecessary String Constructor', 'info',
         'new String() is unnecessary and wasteful',
         'Use string literals directly'),
        (r'String\s*\+\s*String', 'HP090', 'String Concatenation', 'info',
         'String concatenation in loops creates many temporary objects',
         'Use StringBuilder for repeated concatenation'),
        (r'System\.out\.print', 'HP100', 'Console Output in Production', 'info',
         'System.out.print should not be used in production',
         'Use a proper logging framework (SLF4J, Log4j, etc.)'),
    ],
}


class PerformanceAnalyzer(BaseAnalyzer):
    """Analyzes code for performance issues."""

    def __init__(self):
        super().__init__()
        self.supported_languages = list(PERFORMANCE_PATTERNS.keys())
        self._perf_stats: Dict[str, Any] = {}

    def analyze(self, files: List[FileInfo]) -> List[RuleViolation]:
        """Analyze code for performance issues."""
        violations = []
        stats = {
            'total_issues': 0,
            'critical_issues': 0,
            'warning_issues': 0,
            'info_issues': 0,
            'files_affected': 0,
        }

        for file_info in files:
            patterns = PERFORMANCE_PATTERNS.get(file_info.language, [])
            if not patterns:
                continue

            file_has_issues = False
            for i, line in enumerate(file_info.lines):
                stripped = line.strip()
                if not stripped or stripped.startswith('#') or stripped.startswith('//'):
                    continue

                for pattern, rule_id, name, severity, message, suggestion in patterns:
                    if re.search(pattern, stripped):
                        violations.append(self._add_violation(
                            rule_id, name, 'performance', severity,
                            file_info.relative_path, i + 1,
                            message, suggestion, stripped[:80]
                        ))
                        stats['total_issues'] += 1
                        if severity == 'warning':
                            stats['warning_issues'] += 1
                        elif severity == 'info':
                            stats['info_issues'] += 1
                        file_has_issues = True

            if file_has_issues:
                stats['files_affected'] += 1

        self._perf_stats = stats
        self._details = stats
        return violations

    def calculate_score(self, violations: List[RuleViolation],
                         files: List[FileInfo]) -> float:
        """Calculate performance score."""
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
                deductions += 5
            elif v.severity == 'info':
                deductions += 2
            else:
                deductions += 1

        factor = max(1, total_lines / 1000)
        return max(0, min(100, 100 - deductions / factor))
