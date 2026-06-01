"""
Documentation Analyzer - Checks documentation coverage and quality.
"""

import re
from typing import List, Dict, Any
from healthpulse.analyzers import BaseAnalyzer
from healthpulse.scanner import FileInfo
from healthpulse.analyzers import RuleViolation


class DocumentationAnalyzer(BaseAnalyzer):
    """Analyzes documentation coverage and quality."""

    def __init__(self):
        super().__init__()
        self.supported_languages = [
            'python', 'javascript', 'typescript', 'go', 'rust', 'java',
            'ruby', 'php', 'kotlin', 'swift', 'scala', 'shell', 'cpp', 'c',
        ]
        self._doc_stats: Dict[str, Any] = {}

    def analyze(self, files: List[FileInfo]) -> List[RuleViolation]:
        """Analyze documentation coverage."""
        violations = []
        stats = {
            'total_files': 0,
            'files_with_docstrings': 0,
            'files_with_comments': 0,
            'docstring_rate': 0.0,
            'comment_rate': 0.0,
            'has_readme': False,
            'has_license': False,
            'has_changelog': False,
        }

        for file_info in files:
            stats['total_files'] += 1
            file_has_doc = False
            file_has_comments = False

            # Check for docstrings / comments at file level
            for i, line in enumerate(file_info.lines):
                stripped = line.strip()

                # Python docstrings
                if file_info.language == 'python':
                    if stripped.startswith('"""') or stripped.startswith("'''"):
                        file_has_doc = True
                    elif stripped.startswith('#'):
                        file_has_comments = True
                # JS/TS JSDoc
                elif file_info.language in ('javascript', 'typescript'):
                    if stripped.startswith('/**') or stripped.startswith('*'):
                        file_has_doc = True
                    elif stripped.startswith('//'):
                        file_has_comments = True
                # Go doc comments
                elif file_info.language == 'go':
                    if stripped.startswith('//'):
                        file_has_doc = True
                        file_has_comments = True
                # Rust doc comments
                elif file_info.language == 'rust':
                    if stripped.startswith('///') or stripped.startswith('//!'):
                        file_has_doc = True
                    elif stripped.startswith('//'):
                        file_has_comments = True
                # Java docs
                elif file_info.language == 'java':
                    if stripped.startswith('/**') or stripped.startswith('*'):
                        file_has_doc = True
                    elif stripped.startswith('//'):
                        file_has_comments = True
                else:
                    if stripped.startswith('//') or stripped.startswith('#') or stripped.startswith('/*'):
                        file_has_comments = True

            if file_has_doc:
                stats['files_with_docstrings'] += 1
            if file_has_comments:
                stats['files_with_comments'] += 1

            # Check for undocumented public functions/classes
            if file_info.language == 'python':
                violations.extend(self._check_python_docs(file_info))
            elif file_info.language in ('javascript', 'typescript'):
                violations.extend(self._check_js_docs(file_info))

        # Check for project-level docs
        root = files[0].path.parent if files else None
        if root:
            stats['has_readme'] = any(
                f.path.name.lower().startswith('readme') for f in files
            )
            stats['has_license'] = any(
                f.path.name.lower().startswith('license') or f.path.name.lower() == 'licence'
                for f in files
            )
            stats['has_changelog'] = any(
                f.path.name.lower().startswith('change') for f in files
            )

            if not stats['has_readme']:
                violations.append(self._add_violation(
                    'HP070', 'Missing README', 'documentation', 'warning',
                    '.', 1,
                    "No README file found in the project",
                    "Add a README.md with project description, installation, and usage instructions.",
                    ""
                ))

            if not stats['has_license']:
                violations.append(self._add_violation(
                    'HP071', 'Missing LICENSE', 'documentation', 'info',
                    '.', 1,
                    "No LICENSE file found in the project",
                    "Add a LICENSE file to specify the open-source license.",
                    ""
                ))

        if stats['total_files'] > 0:
            stats['docstring_rate'] = round(
                stats['files_with_docstrings'] / stats['total_files'] * 100, 1
            )
            stats['comment_rate'] = round(
                stats['files_with_comments'] / stats['total_files'] * 100, 1
            )

        self._doc_stats = stats
        self._details = stats
        return violations

    def _check_python_docs(self, file: FileInfo) -> List:
        """Check Python documentation."""
        violations = []
        has_module_doc = False
        last_was_def = False

        for i, line in enumerate(file.lines):
            stripped = line.strip()

            # Check module docstring
            if i < 5 and (stripped.startswith('"""') or stripped.startswith("'''")):
                has_module_doc = True

            # Check function/class docstrings
            if re.match(r'^\s*(def|class)\s+\w+', line):
                last_was_def = True
                # Check if next non-empty line is a docstring
                found_doc = False
                for j in range(i + 1, min(i + 4, len(file.lines))):
                    next_stripped = file.lines[j].strip()
                    if not next_stripped:
                        continue
                    if next_stripped.startswith('"""') or next_stripped.startswith("'''"):
                        found_doc = True
                    break

                if not found_doc:
                    match = re.match(r'^\s*(def|class)\s+(\w+)', line)
                    name = match.group(2) if match else 'unknown'
                    violations.append(self._add_violation(
                        'HP072', 'Missing Docstring', 'documentation', 'info',
                        file.relative_path, i + 1,
                        f"Function/class '{name}' is missing a docstring",
                        "Add a docstring describing purpose, parameters, and return value.",
                        stripped[:80]
                    ))

        if not has_module_doc and file.line_count > 10:
            violations.append(self._add_violation(
                'HP073', 'Missing Module Docstring', 'documentation', 'hint',
                file.relative_path, 1,
                "Module is missing a docstring",
                "Add a module-level docstring describing the module's purpose.",
                ""
            ))

        return violations

    def _check_js_docs(self, file: FileInfo) -> List:
        """Check JS/TS documentation."""
        violations = []

        for i, line in enumerate(file.lines):
            stripped = line.strip()

            # Check for function without JSDoc
            if re.search(r'(?:function\s+\w+|(?:const|let|var)\s+\w+\s*=\s*(?:async\s+)?)', line):
                # Check if previous lines have JSDoc
                has_jsdoc = False
                for j in range(max(0, i - 3), i):
                    prev = file.lines[j].strip()
                    if prev.startswith('/**') or (prev.startswith('*') and not prev.startswith('*/')):
                        has_jsdoc = True
                        break

                if not has_jsdoc:
                    match = re.search(r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=)', line)
                    name = match.group(1) or match.group(2) or 'anonymous'
                    violations.append(self._add_violation(
                        'HP074', 'Missing JSDoc', 'documentation', 'hint',
                        file.relative_path, i + 1,
                        f"Function '{name}' is missing JSDoc comments",
                        "Add JSDoc describing purpose, parameters, and return type.",
                        stripped[:80]
                    ))

        return violations

    def calculate_score(self, violations: List[RuleViolation],
                         files: List[FileInfo]) -> float:
        """Calculate documentation score."""
        if not files:
            return 100.0

        # Base score from doc coverage
        doc_rate = self._doc_stats.get('docstring_rate', 0)
        comment_rate = self._doc_stats.get('comment_rate', 0)
        base_score = (doc_rate * 0.6 + comment_rate * 0.4)

        # Deductions for missing project docs
        deductions = 0
        for v in violations:
            if v.severity == 'warning':
                deductions += 10
            elif v.severity == 'info':
                deductions += 3
            else:
                deductions += 1

        return max(0, min(100, base_score - deductions))
