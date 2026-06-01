"""
JSON Reporter - Generates JSON format health report.
"""

import json
from typing import Optional
from healthpulse.engine import DiagnosisResult
from healthpulse.analyzers import RuleViolation
from healthpulse.utils.color import Color


class JSONReporter:
    """JSON format reporter."""

    def __init__(self, color: Optional[Color] = None):
        pass  # JSON doesn't need colors

    def generate(self, diagnosis: DiagnosisResult) -> str:
        """Generate JSON report."""
        report = {
            "healthpulse_version": "1.0.0",
            "overall_score": diagnosis.overall_score,
            "grade": diagnosis.grade,
            "summary": diagnosis.summary,
            "dimensions": {},
            "violations": {
                "total": len(diagnosis.all_violations),
                "critical": diagnosis.critical_count,
                "warning": diagnosis.warning_count,
                "info": diagnosis.info_count,
                "hint": diagnosis.hint_count,
                "items": [],
            },
        }

        # Dimensions
        for dim_name, dim in diagnosis.dimensions.items():
            report["dimensions"][dim_name] = {
                "name": dim.display_name,
                "score": dim.score,
                "weight": dim.weight,
                "weighted_score": dim.weighted_score,
                "violation_count": len(dim.violations),
                "details": dim.details,
            }

        # Violations
        for v in diagnosis.all_violations:
            report["violations"]["items"].append({
                "rule_id": v.rule_id,
                "rule_name": v.rule_name,
                "category": v.category,
                "severity": v.severity,
                "file_path": v.file_path,
                "line_number": v.line_number,
                "message": v.message,
                "suggestion": v.suggestion,
                "code_snippet": v.code_snippet,
            })

        return json.dumps(report, indent=2, ensure_ascii=False)
