"""
Duplication Analyzer - Detects code duplication and copy-paste patterns.
"""

import re
from typing import List, Dict, Any, Tuple
from collections import defaultdict
from healthpulse.analyzers import BaseAnalyzer
from healthpulse.scanner import FileInfo
from healthpulse.analyzers import RuleViolation


class DuplicationAnalyzer(BaseAnalyzer):
    """Analyzes code for duplication patterns."""

    def __init__(self):
        super().__init__()
        self.supported_languages = [
            'python', 'javascript', 'typescript', 'go', 'rust', 'java',
            'ruby', 'php', 'kotlin', 'swift', 'scala', 'shell', 'cpp', 'c',
        ]
        self._dup_stats: Dict[str, Any] = {}

    def analyze(self, files: List[FileInfo]) -> List[RuleViolation]:
        """Analyze code for duplication."""
        violations = []
        stats = {
            'duplicate_blocks': 0,
            'duplicate_lines': 0,
            'duplication_rate': 0.0,
            'total_lines_analyzed': 0,
        }

        total_lines = sum(f.line_count for f in files)
        stats['total_lines_analyzed'] = total_lines

        if total_lines < 10:
            self._dup_stats = stats
            self._details = stats
            return violations

        # Phase 1: Detect duplicated blocks across files
        block_violations, block_stats = self._detect_block_duplication(files)
        violations.extend(block_violations)
        stats['duplicate_blocks'] = block_stats['duplicate_blocks']
        stats['duplicate_lines'] = block_stats['duplicate_lines']

        # Phase 2: Detect similar function signatures
        sig_violations, sig_stats = self._detect_similar_signatures(files)
        violations.extend(sig_violations)

        # Phase 3: Detect repeated patterns within files
        pattern_violations, pattern_stats = self._detect_repeated_patterns(files)
        violations.extend(pattern_violations)

        # Calculate duplication rate
        if total_lines > 0:
            stats['duplication_rate'] = round(
                min(100, (stats['duplicate_lines'] / total_lines) * 100), 1
            )

        self._dup_stats = stats
        self._details = stats
        return violations

    def _normalize_line(self, line: str) -> str:
        """Normalize a line for comparison (remove variable names, values)."""
        normalized = re.sub(r'\b\d+\.?\d*\b', 'N', line)  # Numbers
        normalized = re.sub(r'(["\'])(?:(?!\1).)*\1', 'S', normalized)  # Strings
        normalized = re.sub(r'\b\w+\s*=', 'V=', normalized)  # Variable assignments
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized

    def _get_code_blocks(self, lines: List[str], min_lines: int = 4) -> List[Tuple[int, str]]:
        """Extract code blocks of minimum length for comparison."""
        blocks = []
        normalized_lines = [self._normalize_line(l) for l in lines]

        for i in range(len(normalized_lines) - min_lines + 1):
            block = '\n'.join(normalized_lines[i:i + min_lines])
            if block.strip() and len(block) > 20:
                blocks.append((i, block))

        return blocks

    def _detect_block_duplication(self, files: List[FileInfo]) -> tuple:
        """Detect duplicated code blocks across files."""
        violations = []
        stats = {'duplicate_blocks': 0, 'duplicate_lines': 0}

        # Collect all blocks
        all_blocks = defaultdict(list)
        for file_info in files:
            blocks = self._get_code_blocks(file_info.lines)
            for start_line, block_hash in blocks:
                all_blocks[block_hash].append((file_info, start_line))

        # Find duplicates
        reported_pairs = set()
        for block_hash, locations in all_blocks.items():
            if len(locations) < 2:
                continue

            for i in range(len(locations)):
                for j in range(i + 1, len(locations)):
                    file1, line1 = locations[i]
                    file2, line2 = locations[j]

                    if file1.path == file2.path:
                        continue  # Skip same-file for now

                    pair_key = (file1.relative_path, file2.relative_path, line1)
                    if pair_key in reported_pairs:
                        continue
                    reported_pairs.add(pair_key)

                    stats['duplicate_blocks'] += 1
                    stats['duplicate_lines'] += 4  # block size

                    violations.append(self._add_violation(
                        'HP010', 'Code Duplication', 'duplication', 'warning',
                        file1.relative_path, line1 + 1,
                        f"Duplicated code block found (also in {file2.relative_path}:{line2 + 1})",
                        "Extract duplicated logic into a shared utility function.",
                        self._get_line(file1, line1)
                    ))

        return violations, stats

    def _detect_similar_signatures(self, files: List[FileInfo]) -> tuple:
        """Detect functions with very similar names."""
        violations = []
        stats = {'similar_signatures': 0}

        # Group functions by normalized name pattern
        name_patterns = defaultdict(list)

        for file_info in files:
            if file_info.language == 'python':
                pattern = re.compile(r'def\s+(\w+)')
            elif file_info.language in ('javascript', 'typescript'):
                pattern = re.compile(r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=)')
            elif file_info.language == 'go':
                pattern = re.compile(r'func\s+(?:\([^)]+\)\s+)?(\w+)')
            elif file_info.language == 'rust':
                pattern = re.compile(r'fn\s+(\w+)')
            elif file_info.language == 'java':
                pattern = re.compile(r'(?:public|private|protected)\s+\w+\s+(\w+)\s*\(')
            else:
                continue

            for i, line in enumerate(file_info.lines):
                match = pattern.search(line)
                if match:
                    name = match.group(1) or match.group(2) or ''
                    if name:
                        # Normalize: remove common prefixes/suffixes
                        normalized = re.sub(r'(get|set|is|has|check|validate|handle|process|create|update|delete)_?', '', name)
                        if normalized:
                            name_patterns[normalized].append((file_info, i, name))

        # Find similar names
        for pattern_name, entries in name_patterns.items():
            if len(entries) >= 3:
                stats['similar_signatures'] += 1
                file_info, line, name = entries[0]
                others = [e[2] for e in entries[1:3]]
                violations.append(self._add_violation(
                    'HP011', 'Similar Function Names', 'duplication', 'info',
                    file_info.relative_path, line + 1,
                    f"Multiple similar function names detected: {', '.join([name] + others)}",
                    "Consider consolidating or renaming for clarity.",
                    self._get_line(file_info, line)
                ))

        return violations, stats

    def _detect_repeated_patterns(self, files: List[FileInfo]) -> tuple:
        """Detect repeated code patterns within files."""
        violations = []
        stats = {'repeated_patterns': 0}

        for file_info in files:
            if file_info.line_count < 20:
                continue

            # Count repeated lines
            line_counts = defaultdict(int)
            for line in file_info.lines:
                normalized = self._normalize_line(line)
                if len(normalized) > 15:
                    line_counts[normalized] += 1

            for normalized, count in line_counts.items():
                if count >= 5:
                    stats['repeated_patterns'] += 1
                    # Find first occurrence
                    for i, line in enumerate(file_info.lines):
                        if self._normalize_line(line) == normalized:
                            violations.append(self._add_violation(
                                'HP012', 'Repeated Pattern', 'duplication', 'info',
                                file_info.relative_path, i + 1,
                                f"Similar code pattern repeated {count} times in this file",
                                "Consider using a loop or abstraction to reduce repetition.",
                                line.strip()[:80]
                            ))
                            break

        return violations, stats

    def calculate_score(self, violations: List[RuleViolation],
                         files: List[FileInfo]) -> float:
        """Calculate duplication score."""
        if not files:
            return 100.0

        total_lines = sum(f.line_count for f in files)
        if total_lines == 0:
            return 100.0

        deductions = 0
        for v in violations:
            if v.severity == 'warning':
                deductions += 6
            elif v.severity == 'info':
                deductions += 2
            else:
                deductions += 1

        factor = max(1, total_lines / 1000)
        return max(0, min(100, 100 - deductions / factor))
