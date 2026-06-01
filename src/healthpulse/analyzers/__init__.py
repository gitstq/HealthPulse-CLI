"""
Base Analyzer - Abstract base class for all dimension analyzers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from healthpulse.scanner import FileInfo


@dataclass
class RuleViolation:
    """A single rule violation."""
    rule_id: str
    rule_name: str
    category: str
    severity: str
    file_path: str
    line_number: int
    message: str
    suggestion: str = ""
    code_snippet: str = ""


class BaseAnalyzer(ABC):
    """Abstract base class for dimension analyzers."""

    def __init__(self):
        self.supported_languages: List[str] = []
        self._details: Dict[str, Any] = {}

    @abstractmethod
    def analyze(self, files: List[FileInfo]) -> List[RuleViolation]:
        """Analyze files and return violations."""
        pass

    @abstractmethod
    def calculate_score(self, violations: List[RuleViolation],
                        files: List[FileInfo]) -> float:
        """Calculate dimension score (0-100) based on violations."""
        pass

    def get_details(self) -> Dict[str, Any]:
        """Return detailed analysis metadata."""
        return self._details

    def _add_violation(self, rule_id: str, rule_name: str, category: str,
                        severity: str, file_path: str, line_number: int,
                        message: str, suggestion: str = "",
                        code_snippet: str = "") -> RuleViolation:
        """Helper to create a violation."""
        return RuleViolation(
            rule_id=rule_id,
            rule_name=rule_name,
            category=category,
            severity=severity,
            file_path=file_path,
            line_number=line_number,
            message=message,
            suggestion=suggestion,
            code_snippet=code_snippet,
        )

    def _get_line(self, file: FileInfo, line_num: int) -> str:
        """Get a specific line from file (0-indexed)."""
        if 0 <= line_num < len(file.lines):
            return file.lines[line_num].strip()
        return ""

    def _count_pattern(self, lines: List[str], pattern: str) -> int:
        """Count occurrences of a regex pattern in lines."""
        import re
        count = 0
        for line in lines:
            count += len(re.findall(pattern, line))
        return count
