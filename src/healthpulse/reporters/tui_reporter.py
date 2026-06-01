"""
TUI Reporter - Generates terminal-friendly health report with visual dashboard.
"""

from typing import Optional
from healthpulse.engine import DiagnosisResult
from healthpulse.analyzers import RuleViolation
from healthpulse.utils.color import Color


class TUIReporter:
    """Terminal UI reporter with colored output."""

    def __init__(self, color: Optional[Color] = None):
        self.color = color or Color()

    def generate(self, diagnosis: DiagnosisResult) -> str:
        """Generate TUI report."""
        c = self.color
        lines = []

        # Header
        lines.append(f"\n{c.cyan('╔══════════════════════════════════════════════════════════════╗')}")
        lines.append(f"{c.cyan('║')}  {c.bold_white('🩺 HealthPulse Diagnosis Report')}                              {c.cyan('║')}")
        lines.append(f"{c.cyan('╚══════════════════════════════════════════════════════════════╝')}")
        lines.append("")

        # Overall Score
        score = diagnosis.overall_score
        grade = diagnosis.grade
        lines.append(f"  {c.bold('Overall Health Score')}")
        lines.append(f"  {c.score_color(score)} / 100  {c.grade_color(grade)}")
        lines.append(f"  {c.bar(score)}")
        lines.append("")

        # Summary stats
        s = diagnosis.summary
        lines.append(f"  {c.dim('━' * 55)}")
        lines.append(f"  📊 {c.bold('Summary')}")
        lines.append(f"     Files:    {c.white(str(s.get('total_files', 0)))}")
        lines.append(f"     Lines:    {c.white(str(s.get('total_lines', 0)))}")
        lines.append(f"     Size:     {c.white(str(s.get('total_size_kb', 0)))} KB")
        if s.get('primary_language'):
            lines.append(f"     Language: {c.white(s['primary_language'])}")
        if s.get('languages'):
            lang_str = ', '.join(f"{lang} ({count})" for lang, count in sorted(s['languages'].items(), key=lambda x: -x[1])[:5])
            lines.append(f"     Breakdown: {c.dim(lang_str)}")
        scan_time_str = f"{s.get('scan_time', 0):.2f}s"
        diag_time_str = f"{s.get('diagnosis_time', 0):.2f}s"
        lines.append(f"     Scan:     {c.dim(scan_time_str)}")
        lines.append(f"     Analysis: {c.dim(diag_time_str)}")
        lines.append("")

        # Violation summary
        lines.append(f"  {c.dim('━' * 55)}")
        lines.append(f"  📋 {c.bold('Issues Found')}")
        lines.append(f"     {c.bold_red(str(diagnosis.critical_count))} Critical   "
                     f"{c.bold_yellow(str(diagnosis.warning_count))} Warning   "
                     f"{c.blue(str(diagnosis.info_count))} Info   "
                     f"{c.dim(str(diagnosis.hint_count))} Hint")
        lines.append(f"     Total: {c.white(str(len(diagnosis.all_violations)))}")
        lines.append("")

        # Dimension scores
        lines.append(f"  {c.dim('━' * 55)}")
        lines.append(f"  📐 {c.bold('Dimension Scores')}")
        lines.append("")

        dim_order = [
            'complexity', 'duplication', 'naming', 'security',
            'architecture', 'documentation', 'maintainability', 'performance'
        ]

        for dim_name in dim_order:
            dim = diagnosis.dimensions.get(dim_name)
            if dim is None:
                continue

            score = dim.score
            bar = c.bar(score, 15)
            lines.append(f"  {c.bold(dim.display_name):<18} {c.score_color(score):>5}  {bar}")

        lines.append("")

        # Top violations
        if diagnosis.all_violations:
            lines.append(f"  {c.dim('━' * 55)}")
            lines.append(f"  ⚠️  {c.bold('Top Issues')} (max 15)")
            lines.append("")

            # Sort by severity
            severity_order = {'critical': 0, 'warning': 1, 'info': 2, 'hint': 3}
            sorted_violations = sorted(
                diagnosis.all_violations,
                key=lambda v: (severity_order.get(v.severity, 99), v.rule_id)
            )

            for v in sorted_violations[:15]:
                sev = c.severity_color(v.severity)
                lines.append(f"  {sev} [{v.rule_id}] {c.white(v.message)}")
                loc_str = f"  {v.file_path}:{v.line_number}"
                lines.append(f"    {c.dim(loc_str)}")
                if v.suggestion:
                    sug_str = f"  {v.suggestion}"
                    lines.append(f"    {c.dim(sug_str)}")
                lines.append("")

        # Footer
        lines.append(f"  {c.dim('━' * 55)}")
        lines.append(f"  {c.dim('Powered by HealthPulse-CLI v1.0.0 | GLM-5.1')}")
        lines.append("")

        return '\n'.join(lines)
