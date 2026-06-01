"""
Markdown Reporter - Generates Markdown format health report.
"""

from typing import Optional
from healthpulse.engine import DiagnosisResult
from healthpulse.analyzers import RuleViolation
from healthpulse.utils.color import Color


class MarkdownReporter:
    """Markdown format reporter."""

    def __init__(self, color: Optional[Color] = None):
        pass

    def generate(self, diagnosis: DiagnosisResult) -> str:
        """Generate Markdown report."""
        score = diagnosis.overall_score
        grade = diagnosis.grade
        s = diagnosis.summary

        if score >= 80:
            badge = '🟢'
        elif score >= 60:
            badge = '🟡'
        elif score >= 40:
            badge = '🔵'
        else:
            badge = '🔴'

        lines = [
            f"# 🩺 HealthPulse Diagnosis Report",
            "",
            f"{badge} **Overall Score: {score}/100** | Grade: **{grade}**",
            "",
            "## 📊 Summary",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Files | {s.get('total_files', 0)} |",
            f"| Lines | {s.get('total_lines', 0)} |",
            f"| Size | {s.get('total_size_kb', 0)} KB |",
            f"| Primary Language | {s.get('primary_language', 'N/A')} |",
            f"| Total Issues | {len(diagnosis.all_violations)} |",
            f"| Critical | 🔴 {diagnosis.critical_count} |",
            f"| Warning | 🟡 {diagnosis.warning_count} |",
            f"| Info | 🔵 {diagnosis.info_count} |",
            f"| Hint | ⚪ {diagnosis.hint_count} |",
            "",
            "## 📐 Dimension Scores",
            "",
            "| Dimension | Score | Issues |",
            "|-----------|-------|--------|",
        ]

        for dim_name in ['complexity', 'duplication', 'naming', 'security',
                         'architecture', 'documentation', 'maintainability', 'performance']:
            dim = diagnosis.dimensions.get(dim_name)
            if dim:
                if dim.score >= 80:
                    emoji = '🟢'
                elif dim.score >= 60:
                    emoji = '🟡'
                elif dim.score >= 40:
                    emoji = '🔵'
                else:
                    emoji = '🔴'
                lines.append(f"| {dim.display_name} | {emoji} {dim.score} | {len(dim.violations)} |")

        # Top violations
        if diagnosis.all_violations:
            lines.extend([
                "",
                "## ⚠️ Top Issues",
                "",
            ])

            severity_order = {'critical': 0, 'warning': 1, 'info': 2, 'hint': 3}
            sorted_violations = sorted(
                diagnosis.all_violations,
                key=lambda v: (severity_order.get(v.severity, 99), v.rule_id)
            )

            severity_emoji = {
                'critical': '🔴',
                'warning': '🟡',
                'info': '🔵',
                'hint': '⚪',
            }

            for v in sorted_violations[:30]:
                emoji = severity_emoji.get(v.severity, '⚪')
                lines.append(f"### {emoji} [{v.rule_id}] {v.message}")
                lines.append(f"- **File:** `{v.file_path}:{v.line_number}`")
                lines.append(f"- **Category:** {v.category}")
                if v.suggestion:
                    lines.append(f"- **Suggestion:** {v.suggestion}")
                lines.append("")

        lines.extend([
            "---",
            "",
            "*Powered by HealthPulse-CLI v1.0.0 | GLM-5.1*",
        ])

        return '\n'.join(lines)
