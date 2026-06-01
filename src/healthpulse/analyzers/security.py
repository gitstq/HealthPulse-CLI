"""
Security Analyzer - Detects common security vulnerabilities and anti-patterns.
"""

import re
from typing import List, Dict, Any
from healthpulse.analyzers import BaseAnalyzer
from healthpulse.scanner import FileInfo
from healthpulse.analyzers import RuleViolation


# Security patterns by language
SECURITY_PATTERNS = {
    'python': [
        (r'eval\s*\(', 'HP030', 'Dangerous eval()', 'critical',
         'Use of eval() can lead to arbitrary code execution',
         'Use ast.literal_eval() for safe evaluation or avoid eval() entirely'),
        (r'exec\s*\(', 'HP031', 'Dangerous exec()', 'critical',
         'Use of exec() can lead to arbitrary code execution',
         'Avoid exec() or use safer alternatives'),
        (r'pickle\.loads?\s*\(', 'HP032', 'Unsafe Pickle Deserialization', 'critical',
         'Pickle deserialization can execute arbitrary code',
         'Use JSON or safer serialization formats'),
        (r'subprocess\.call\s*\([^)]*shell\s*=\s*True', 'HP033', 'Shell Injection Risk', 'critical',
         'subprocess with shell=True can lead to command injection',
         'Use subprocess.run() with list arguments instead of shell=True'),
        (r'os\.system\s*\(', 'HP034', 'OS Command Injection', 'warning',
         'os.system() is vulnerable to command injection',
         'Use subprocess.run() with list arguments'),
        (r'input\s*\(', 'HP035', 'Input Without Validation', 'info',
         'input() without validation can be a security risk',
         'Validate and sanitize all user input'),
        (r'password\s*=\s*["\'][^"\']+["\']', 'HP036', 'Hardcoded Password', 'critical',
         'Hardcoded password detected in source code',
         'Use environment variables or a secrets manager'),
        (r'api_key\s*=\s*["\'][^"\']+["\']', 'HP037', 'Hardcoded API Key', 'critical',
         'Hardcoded API key detected in source code',
         'Use environment variables or a secrets manager'),
        (r'secret\s*=\s*["\'][^"\']+["\']', 'HP038', 'Hardcoded Secret', 'critical',
         'Hardcoded secret detected in source code',
         'Use environment variables or a secrets manager'),
        (r'token\s*=\s*["\'][^"\']+["\']', 'HP039', 'Hardcoded Token', 'warning',
         'Hardcoded token detected in source code',
         'Use environment variables or a secrets manager'),
        (r'assert\s+', 'HP040', 'Assert for Security Check', 'warning',
         'Assert statements are removed with -O flag, unsafe for security',
         'Use explicit if/raise checks for security validations'),
        (r'md5\s*\(|MD5', 'HP041', 'Weak Hash Algorithm', 'warning',
         'MD5 is cryptographically broken',
         'Use hashlib.sha256() or stronger algorithms'),
        (r'sha1\s*\(|SHA1', 'HP042', 'Weak Hash Algorithm', 'info',
         'SHA-1 is deprecated for cryptographic use',
         'Use SHA-256 or stronger algorithms'),
        (r'except\s*:', 'HP043', 'Bare Except', 'warning',
         'Bare except catches all exceptions including KeyboardInterrupt',
         'Use specific exception types like except Exception:'),
        (r'__import__\s*\(', 'HP044', 'Dynamic Import', 'warning',
         'Dynamic imports can be a security risk',
         'Use explicit imports when possible'),
    ],
    'javascript': [
        (r'eval\s*\(', 'HP030', 'Dangerous eval()', 'critical',
         'eval() can execute arbitrary code',
         'Use JSON.parse() or safer alternatives'),
        (r'document\.write\s*\(', 'HP045', 'DOM XSS Risk', 'warning',
         'document.write() can lead to XSS vulnerabilities',
         'Use textContent or innerHTML with sanitization'),
        (r'innerHTML\s*=', 'HP046', 'innerHTML Assignment', 'warning',
         'Direct innerHTML assignment can lead to XSS',
         'Use textContent or sanitize HTML before assignment'),
        (r'new\s+Function\s*\(', 'HP047', 'Dynamic Function Constructor', 'critical',
         'Function constructor is equivalent to eval()',
         'Use proper function definitions'),
        (r'password\s*[:=]\s*["\'][^"\']+["\']', 'HP036', 'Hardcoded Password', 'critical',
         'Hardcoded password in source code',
         'Use environment variables'),
        (r'api_?key\s*[:=]\s*["\'][^"\']+["\']', 'HP037', 'Hardcoded API Key', 'critical',
         'Hardcoded API key in source code',
         'Use environment variables'),
        (r'\.exec\s*\(', 'HP048', 'Shell Command Execution', 'warning',
         'Child process execution detected',
         'Validate and sanitize all inputs'),
        (r'localStorage\.getItem|sessionStorage\.getItem', 'HP049', 'Storage Access', 'info',
         'Direct storage access without validation',
         'Validate data from storage before use'),
    ],
    'typescript': [
        (r'eval\s*\(', 'HP030', 'Dangerous eval()', 'critical',
         'eval() can execute arbitrary code',
         'Use JSON.parse() or safer alternatives'),
        (r'password\s*[:=]\s*["\'][^"\']+["\']', 'HP036', 'Hardcoded Password', 'critical',
         'Hardcoded password in source code',
         'Use environment variables'),
        (r'api_?key\s*[:=]\s*["\'][^"\']+["\']', 'HP037', 'Hardcoded API Key', 'critical',
         'Hardcoded API key in source code',
         'Use environment variables'),
        (r'any\s*[,)\]]', 'HP050', 'Type Safety Bypass', 'info',
         'Use of "any" type bypasses TypeScript type checking',
         'Use specific types or unknown instead'),
    ],
    'go': [
        (r'exec\.Command\s*\(', 'HP051', 'Command Execution', 'warning',
         'Direct command execution detected',
         'Validate all inputs and avoid shell injection'),
        (r'password\s*[:=]\s*["\'][^"\']+["\']', 'HP036', 'Hardcoded Password', 'critical',
         'Hardcoded password in source code',
         'Use environment variables'),
        (r'md5\.', 'HP041', 'Weak Hash Algorithm', 'warning',
         'MD5 is cryptographically broken',
         'Use crypto/sha256 or stronger'),
    ],
    'rust': [
        (r'unsafe\s*\{', 'HP052', 'Unsafe Block', 'warning',
         'Unsafe Rust code bypasses safety guarantees',
         'Minimize unsafe blocks and document safety invariants'),
        (r'password\s*[:=]\s*["\'][^"\']+["\']', 'HP036', 'Hardcoded Password', 'critical',
         'Hardcoded password in source code',
         'Use environment variables'),
    ],
    'java': [
        (r'Runtime\.getRuntime\(\)\.exec\s*\(', 'HP053', 'Runtime Command Execution', 'critical',
         'Runtime.exec() can lead to command injection',
         'Use ProcessBuilder with proper input validation'),
        (r'password\s*=\s*["\'][^"\']+["\']', 'HP036', 'Hardcoded Password', 'critical',
         'Hardcoded password in source code',
         'Use environment variables or vault'),
        (r'MessageDigest\.getInstance\s*\(\s*["\']MD5["\']', 'HP041', 'Weak Hash Algorithm', 'warning',
         'MD5 is cryptographically broken',
         'Use SHA-256 or stronger'),
    ],
}


class SecurityAnalyzer(BaseAnalyzer):
    """Analyzes code for security vulnerabilities."""

    def __init__(self):
        super().__init__()
        self.supported_languages = list(SECURITY_PATTERNS.keys())
        self._security_stats: Dict[str, Any] = {}

    def analyze(self, files: List[FileInfo]) -> List[RuleViolation]:
        """Analyze code for security issues."""
        violations = []
        stats = {
            'critical_issues': 0,
            'warning_issues': 0,
            'info_issues': 0,
            'files_with_issues': 0,
        }

        for file_info in files:
            patterns = SECURITY_PATTERNS.get(file_info.language, [])
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
                            rule_id, name, 'security', severity,
                            file_info.relative_path, i + 1,
                            message, suggestion, stripped[:80]
                        ))

                        if severity == 'critical':
                            stats['critical_issues'] += 1
                        elif severity == 'warning':
                            stats['warning_issues'] += 1
                        else:
                            stats['info_issues'] += 1

                        file_has_issues = True

            if file_has_issues:
                stats['files_with_issues'] += 1

        self._security_stats = stats
        self._details = stats
        return violations

    def calculate_score(self, violations: List[RuleViolation],
                         files: List[FileInfo]) -> float:
        """Calculate security score."""
        if not files:
            return 100.0

        total_lines = sum(f.line_count for f in files)
        if total_lines == 0:
            return 100.0

        deductions = 0
        for v in violations:
            if v.severity == 'critical':
                deductions += 15
            elif v.severity == 'warning':
                deductions += 8
            elif v.severity == 'info':
                deductions += 3
            else:
                deductions += 1

        factor = max(1, total_lines / 1000)
        return max(0, min(100, 100 - deductions / factor))
