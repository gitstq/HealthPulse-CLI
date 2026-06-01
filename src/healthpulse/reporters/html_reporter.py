"""
HTML Reporter - Generates HTML format health report.
"""

import json
from typing import Optional
from healthpulse.engine import DiagnosisResult
from healthpulse.analyzers import RuleViolation
from healthpulse.utils.color import Color


class HTMLReporter:
    """HTML format reporter."""

    def __init__(self, color: Optional[Color] = None):
        pass

    def generate(self, diagnosis: DiagnosisResult) -> str:
        """Generate HTML report."""
        score = diagnosis.overall_score
        grade = diagnosis.grade

        if score >= 80:
            score_color = '#22c55e'
            score_bg = '#f0fdf4'
        elif score >= 60:
            score_color = '#eab308'
            score_bg = '#fefce8'
        elif score >= 40:
            score_color = '#3b82f6'
            score_bg = '#eff6ff'
        else:
            score_color = '#ef4444'
            score_bg = '#fef2f2'

        # Build dimension rows
        dim_rows = ""
        for dim_name, dim in diagnosis.dimensions.items():
            dim_score = dim.score
            if dim_score >= 80:
                bar_color = '#22c55e'
            elif dim_score >= 60:
                bar_color = '#eab308'
            elif dim_score >= 40:
                bar_color = '#3b82f6'
            else:
                bar_color = '#ef4444'

            dim_rows += f"""
            <tr>
                <td><strong>{dim.display_name}</strong></td>
                <td style="text-align:center;font-weight:bold;color:{bar_color}">{dim_score}</td>
                <td>
                    <div style="background:#e5e7eb;border-radius:4px;height:20px;overflow:hidden">
                        <div style="background:{bar_color};width:{dim_score}%;height:100%;border-radius:4px"></div>
                    </div>
                </td>
                <td style="text-align:center">{len(dim.violations)}</td>
            </tr>"""

        # Build violation rows
        violation_rows = ""
        severity_order = {'critical': 0, 'warning': 1, 'info': 2, 'hint': 3}
        sorted_violations = sorted(
            diagnosis.all_violations,
            key=lambda v: (severity_order.get(v.severity, 99), v.rule_id)
        )

        severity_badge = {
            'critical': ('#ef4444', '#fef2f2'),
            'warning': ('#eab308', '#fefce8'),
            'info': ('#3b82f6', '#eff6ff'),
            'hint': ('#6b7280', '#f9fafb'),
        }

        for v in sorted_violations[:50]:
            text_color, bg_color = severity_badge.get(v.severity, ('#6b7280', '#f9fafb'))
            violation_rows += f"""
            <tr>
                <td><span style="background:{bg_color};color:{text_color};padding:2px 8px;border-radius:4px;font-size:12px;font-weight:bold">{v.severity.upper()}</span></td>
                <td><code>{v.rule_id}</code></td>
                <td>{v.message}</td>
                <td><code style="font-size:12px">{v.file_path}:{v.line_number}</code></td>
            </tr>"""

        s = diagnosis.summary
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HealthPulse Report - Score: {score}/100 ({grade})</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8fafc; color: #1e293b; padding: 20px; }}
        .container {{ max-width: 960px; margin: 0 auto; }}
        .header {{ text-align: center; padding: 30px; background: white; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .score-circle {{ width: 120px; height: 120px; border-radius: 50%; background: {score_bg}; border: 4px solid {score_color}; display: inline-flex; align-items: center; justify-content: center; margin: 15px 0; }}
        .score-value {{ font-size: 36px; font-weight: bold; color: {score_color}; }}
        .grade {{ font-size: 24px; font-weight: bold; color: {score_color}; margin-top: 5px; }}
        .card {{ background: white; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 20px; margin-bottom: 20px; }}
        .card h2 {{ font-size: 18px; margin-bottom: 15px; color: #334155; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; }}
        .stat {{ text-align: center; padding: 15px; background: #f8fafc; border-radius: 8px; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #334155; }}
        .stat-label {{ font-size: 12px; color: #64748b; margin-top: 4px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{ text-align: left; padding: 10px 12px; background: #f8fafc; font-size: 13px; color: #64748b; border-bottom: 2px solid #e2e8f0; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #f1f5f9; font-size: 14px; }}
        tr:hover {{ background: #f8fafc; }}
        code {{ background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 13px; }}
        .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
        .footer {{ text-align: center; padding: 20px; color: #94a3b8; font-size: 13px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🩺 HealthPulse Diagnosis Report</h1>
            <div class="score-circle">
                <div class="score-value">{score}</div>
            </div>
            <div class="grade">Grade: {grade}</div>
            <p style="color:#64748b;margin-top:10px">Code Repository Health Diagnosis</p>
        </div>

        <div class="card">
            <h2>📊 Summary</h2>
            <div class="stats">
                <div class="stat"><div class="stat-value">{s.get('total_files', 0)}</div><div class="stat-label">Files</div></div>
                <div class="stat"><div class="stat-value">{s.get('total_lines', 0)}</div><div class="stat-label">Lines</div></div>
                <div class="stat"><div class="stat-value">{s.get('total_size_kb', 0)} KB</div><div class="stat-label">Size</div></div>
                <div class="stat"><div class="stat-value">{len(diagnosis.all_violations)}</div><div class="stat-label">Issues</div></div>
                <div class="stat"><div class="stat-value" style="color:#ef4444">{diagnosis.critical_count}</div><div class="stat-label">Critical</div></div>
                <div class="stat"><div class="stat-value" style="color:#eab308">{diagnosis.warning_count}</div><div class="stat-label">Warning</div></div>
            </div>
        </div>

        <div class="card">
            <h2>📐 Dimension Scores</h2>
            <table>
                <thead><tr><th>Dimension</th><th style="text-align:center">Score</th><th>Progress</th><th style="text-align:center">Issues</th></tr></thead>
                <tbody>{dim_rows}</tbody>
            </table>
        </div>

        <div class="card">
            <h2>⚠️ Issues ({len(diagnosis.all_violations)} total)</h2>
            <table>
                <thead><tr><th>Severity</th><th>Rule</th><th>Message</th><th>Location</th></tr></thead>
                <tbody>{violation_rows}</tbody>
            </table>
        </div>

        <div class="footer">
            Powered by HealthPulse-CLI v1.0.0 | GLM-5.1
        </div>
    </div>
</body>
</html>"""
        return html
