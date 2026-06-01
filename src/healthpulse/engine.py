"""
Diagnosis Engine - Core engine that applies rules and calculates health scores.
"""

import time
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from healthpulse.scanner import ScanResult, FileInfo
from healthpulse.analyzers import RuleViolation
from healthpulse.analyzers.complexity import ComplexityAnalyzer
from healthpulse.analyzers.duplication import DuplicationAnalyzer
from healthpulse.analyzers.naming import NamingAnalyzer
from healthpulse.analyzers.security import SecurityAnalyzer
from healthpulse.analyzers.architecture import ArchitectureAnalyzer
from healthpulse.analyzers.documentation import DocumentationAnalyzer
from healthpulse.analyzers.maintainability import MaintainabilityAnalyzer
from healthpulse.analyzers.performance import PerformanceAnalyzer


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


@dataclass
class DimensionScore:
    """Score for a single dimension."""
    name: str
    display_name: str
    score: float  # 0-100
    weight: float
    violations: List[RuleViolation] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

    @property
    def weighted_score(self) -> float:
        return self.score * self.weight


@dataclass
class DiagnosisResult:
    """Complete diagnosis result."""
    overall_score: float = 0.0
    grade: str = "F"
    dimensions: Dict[str, DimensionScore] = field(default_factory=dict)
    all_violations: List[RuleViolation] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    scan_result: Optional[ScanResult] = None
    diagnosis_time: float = 0.0

    @property
    def critical_count(self) -> int:
        return sum(1 for v in self.all_violations if v.severity == 'critical')

    @property
    def warning_count(self) -> int:
        return sum(1 for v in self.all_violations if v.severity == 'warning')

    @property
    def info_count(self) -> int:
        return sum(1 for v in self.all_violations if v.severity == 'info')

    @property
    def hint_count(self) -> int:
        return sum(1 for v in self.all_violations if v.severity == 'hint')


class DiagnosisEngine:
    """Core diagnosis engine that orchestrates all analyzers."""

    DIMENSION_CONFIG = {
        'complexity': {'display': 'Complexity', 'weight': 1.0},
        'duplication': {'display': 'Duplication', 'weight': 1.0},
        'naming': {'display': 'Naming', 'weight': 0.8},
        'security': {'display': 'Security', 'weight': 1.2},
        'architecture': {'display': 'Architecture', 'weight': 0.9},
        'documentation': {'display': 'Documentation', 'weight': 0.7},
        'maintainability': {'display': 'Maintainability', 'weight': 1.0},
        'performance': {'display': 'Performance', 'weight': 0.8},
    }

    def __init__(self, rules_filter: Optional[str] = None, verbose: bool = False):
        self.rules_filter = rules_filter
        self.verbose = verbose
        self.analyzers = {
            'complexity': ComplexityAnalyzer(),
            'duplication': DuplicationAnalyzer(),
            'naming': NamingAnalyzer(),
            'security': SecurityAnalyzer(),
            'architecture': ArchitectureAnalyzer(),
            'documentation': DocumentationAnalyzer(),
            'maintainability': MaintainabilityAnalyzer(),
            'performance': PerformanceAnalyzer(),
        }

    def diagnose(self, scan_result: ScanResult) -> DiagnosisResult:
        """Run full diagnosis on scan results."""
        start_time = time.time()
        result = DiagnosisResult(scan_result=scan_result)

        total_weight = sum(cfg['weight'] for cfg in self.DIMENSION_CONFIG.values())
        weighted_sum = 0.0

        for dim_name, analyzer in self.analyzers.items():
            config = self.DIMENSION_CONFIG[dim_name]

            # Filter files by language support
            compatible_files = [
                f for f in scan_result.files
                if f.language in analyzer.supported_languages
            ]

            if not compatible_files:
                dim_score = DimensionScore(
                    name=dim_name,
                    display_name=config['display'],
                    score=100.0,
                    weight=config['weight'],
                )
                result.dimensions[dim_name] = dim_score
                weighted_sum += 100.0 * config['weight']
                continue

            # Run analyzer
            violations = analyzer.analyze(compatible_files)
            score = analyzer.calculate_score(violations, compatible_files)

            dim_score = DimensionScore(
                name=dim_name,
                display_name=config['display'],
                score=max(0, min(100, score)),
                weight=config['weight'],
                violations=violations,
                details=analyzer.get_details(),
            )
            result.dimensions[dim_name] = dim_score
            result.all_violations.extend(violations)
            weighted_sum += dim_score.weighted_score

        # Calculate overall score
        result.overall_score = round(weighted_sum / total_weight, 1) if total_weight > 0 else 0
        result.grade = self._calculate_grade(result.overall_score)

        # Build summary
        result.summary = {
            'total_files': scan_result.total_files,
            'total_lines': scan_result.total_lines,
            'total_size_kb': round(scan_result.total_size / 1024, 1),
            'languages': scan_result.languages,
            'primary_language': scan_result.primary_language,
            'scan_time': scan_result.scan_time,
            'diagnosis_time': time.time() - start_time,
        }

        result.diagnosis_time = time.time() - start_time
        return result

    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from score."""
        if score >= 90:
            return 'A+'
        elif score >= 85:
            return 'A'
        elif score >= 80:
            return 'A-'
        elif score >= 75:
            return 'B+'
        elif score >= 70:
            return 'B'
        elif score >= 65:
            return 'B-'
        elif score >= 60:
            return 'C+'
        elif score >= 55:
            return 'C'
        elif score >= 50:
            return 'C-'
        elif score >= 40:
            return 'D'
        else:
            return 'F'
