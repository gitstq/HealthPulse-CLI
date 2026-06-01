"""
Rule Registry - Manages all diagnosis rules.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Rule:
    """Represents a single diagnosis rule."""
    rule_id: str
    name: str
    category: str
    severity: str
    description: str
    languages: List[str]
    suggestion: str = ""


class RuleRegistry:
    """Registry of all diagnosis rules."""

    _rules: List[Rule] = []

    @classmethod
    def _init_rules(cls):
        """Initialize all rules."""
        if cls._rules:
            return

        all_langs = ['python', 'javascript', 'typescript', 'go', 'rust', 'java',
                     'ruby', 'php', 'kotlin', 'swift', 'scala', 'shell', 'cpp', 'c']

        cls._rules = [
            # Complexity
            Rule('HP001', 'Deep Nesting', 'complexity', 'warning',
                 'Detects deeply nested code structures (>6 levels)', all_langs,
                 'Extract nested logic into helper functions'),
            Rule('HP002', 'High Cyclomatic Complexity', 'complexity', 'warning',
                 'Functions with cyclomatic complexity > 10', all_langs,
                 'Break down complex functions into smaller ones'),
            Rule('HP003', 'Long Function', 'complexity', 'warning',
                 'Functions exceeding 50 lines', all_langs,
                 'Extract logical blocks into separate functions'),
            Rule('HP004', 'Too Many Parameters', 'complexity', 'info',
                 'Functions with more than 5 parameters', all_langs,
                 'Use a data class or options object'),
            Rule('HP008', 'Long Line', 'complexity', 'info',
                 'Lines exceeding 150 characters', all_langs,
                 'Break long lines into multiple statements'),

            # Duplication
            Rule('HP010', 'Code Duplication', 'duplication', 'warning',
                 'Duplicated code blocks across files', all_langs,
                 'Extract shared logic into utility functions'),
            Rule('HP011', 'Similar Function Names', 'duplication', 'info',
                 'Multiple functions with very similar names', all_langs,
                 'Consolidate or rename for clarity'),
            Rule('HP012', 'Repeated Pattern', 'duplication', 'info',
                 'Similar code pattern repeated 5+ times', all_langs,
                 'Use loops or abstractions to reduce repetition'),

            # Naming
            Rule('HP020', 'Naming Convention Violation', 'naming', 'info',
                 'Names not following language conventions',
                 ['python', 'javascript', 'typescript', 'go', 'rust', 'java'],
                 'Follow the language naming convention'),
            Rule('HP021', 'Poor Name Choice', 'naming', 'hint',
                 'Generic or uninformative names', all_langs,
                 'Use descriptive names that convey purpose'),

            # Security
            Rule('HP030', 'Dangerous eval()', 'security', 'critical',
                 'Use of eval() can execute arbitrary code',
                 ['python', 'javascript', 'typescript'],
                 'Use safer alternatives like JSON.parse()'),
            Rule('HP031', 'Dangerous exec()', 'security', 'critical',
                 'Use of exec() can execute arbitrary code', ['python'],
                 'Avoid exec() or use safer alternatives'),
            Rule('HP032', 'Unsafe Pickle Deserialization', 'security', 'critical',
                 'Pickle deserialization can execute arbitrary code', ['python'],
                 'Use JSON or safer serialization'),
            Rule('HP033', 'Shell Injection Risk', 'security', 'critical',
                 'subprocess with shell=True can lead to injection', ['python'],
                 'Use list arguments instead of shell=True'),
            Rule('HP034', 'OS Command Injection', 'security', 'warning',
                 'os.system() is vulnerable to command injection', ['python'],
                 'Use subprocess.run() with list arguments'),
            Rule('HP035', 'Input Without Validation', 'security', 'info',
                 'input() without validation can be a security risk', ['python'],
                 'Validate and sanitize all user input'),
            Rule('HP036', 'Hardcoded Password', 'security', 'critical',
                 'Hardcoded password in source code', all_langs,
                 'Use environment variables or secrets manager'),
            Rule('HP037', 'Hardcoded API Key', 'security', 'critical',
                 'Hardcoded API key in source code', all_langs,
                 'Use environment variables or secrets manager'),
            Rule('HP038', 'Hardcoded Secret', 'security', 'critical',
                 'Hardcoded secret in source code', all_langs,
                 'Use environment variables or secrets manager'),
            Rule('HP039', 'Hardcoded Token', 'security', 'warning',
                 'Hardcoded token in source code', all_langs,
                 'Use environment variables or secrets manager'),
            Rule('HP040', 'Assert for Security Check', 'security', 'warning',
                 'Assert statements removed with -O flag', ['python'],
                 'Use explicit if/raise for security checks'),
            Rule('HP041', 'Weak Hash Algorithm (MD5)', 'security', 'warning',
                 'MD5 is cryptographically broken',
                 ['python', 'go', 'java'],
                 'Use SHA-256 or stronger algorithms'),
            Rule('HP042', 'Weak Hash Algorithm (SHA1)', 'security', 'info',
                 'SHA-1 is deprecated for crypto use', ['python'],
                 'Use SHA-256 or stronger algorithms'),
            Rule('HP043', 'Bare Except', 'security', 'warning',
                 'Bare except catches all exceptions', ['python'],
                 'Use specific exception types'),
            Rule('HP044', 'Dynamic Import', 'security', 'warning',
                 'Dynamic imports can be a security risk', ['python'],
                 'Use explicit imports when possible'),
            Rule('HP045', 'DOM XSS Risk', 'security', 'warning',
                 'document.write() can lead to XSS', ['javascript'],
                 'Use textContent or sanitized innerHTML'),
            Rule('HP046', 'innerHTML Assignment', 'security', 'warning',
                 'Direct innerHTML assignment XSS risk', ['javascript'],
                 'Use textContent or sanitize HTML'),
            Rule('HP047', 'Dynamic Function Constructor', 'security', 'critical',
                 'Function constructor equivalent to eval()', ['javascript'],
                 'Use proper function definitions'),
            Rule('HP048', 'Shell Command Execution', 'security', 'warning',
                 'Child process execution detected', ['javascript', 'typescript'],
                 'Validate and sanitize all inputs'),
            Rule('HP049', 'Storage Access', 'security', 'info',
                 'Direct storage access without validation', ['javascript', 'typescript'],
                 'Validate data from storage before use'),
            Rule('HP050', 'Type Safety Bypass', 'security', 'info',
                 'Use of "any" bypasses type checking', ['typescript'],
                 'Use specific types or unknown'),
            Rule('HP051', 'Command Execution', 'security', 'warning',
                 'Direct command execution detected', ['go'],
                 'Validate all inputs'),
            Rule('HP052', 'Unsafe Block', 'security', 'warning',
                 'Unsafe code bypasses safety guarantees', ['rust'],
                 'Minimize unsafe blocks'),
            Rule('HP053', 'Runtime Command Execution', 'security', 'critical',
                 'Runtime.exec() can lead to injection', ['java'],
                 'Use ProcessBuilder with validation'),

            # Architecture
            Rule('HP060', 'Large File', 'architecture', 'warning',
                 'Files exceeding 500 lines', all_langs,
                 'Split into smaller, focused modules'),
            Rule('HP061', 'God Class', 'architecture', 'warning',
                 'Single file with too many methods', ['python'],
                 'Split into smaller, focused classes'),
            Rule('HP062', 'Flat Directory Structure', 'architecture', 'info',
                 'Too many files in root directory', all_langs,
                 'Organize into subdirectories'),
            Rule('HP063', 'Missing __init__.py', 'architecture', 'info',
                 'Python package missing __init__.py', ['python'],
                 'Add __init__.py to make it a proper package'),
            Rule('HP064', 'High Coupling', 'architecture', 'info',
                 'Module imported by too many files', all_langs,
                 'Introduce abstraction layer'),

            # Documentation
            Rule('HP070', 'Missing README', 'documentation', 'warning',
                 'No README file found', all_langs,
                 'Add a README.md with project docs'),
            Rule('HP071', 'Missing LICENSE', 'documentation', 'info',
                 'No LICENSE file found', all_langs,
                 'Add a LICENSE file'),
            Rule('HP072', 'Missing Docstring', 'documentation', 'info',
                 'Function/class missing docstring', ['python'],
                 'Add docstring with purpose and params'),
            Rule('HP073', 'Missing Module Docstring', 'documentation', 'hint',
                 'Module missing docstring', ['python'],
                 'Add module-level docstring'),
            Rule('HP074', 'Missing JSDoc', 'documentation', 'hint',
                 'Function missing JSDoc', ['javascript', 'typescript'],
                 'Add JSDoc with description and types'),

            # Maintainability
            Rule('HP080', 'Excessive Long Lines', 'maintainability', 'info',
                 'Too many long lines in file', all_langs,
                 'Keep lines under 120 characters'),
            Rule('HP081', 'TODO Found', 'maintainability', 'hint',
                 'TODO comment found', all_langs,
                 'Resolve TODO or create issue'),
            Rule('HP082', 'FIXME Found', 'maintainability', 'warning',
                 'FIXME comment indicates known issue', all_langs,
                 'Fix the issue and remove FIXME'),
            Rule('HP083', 'HACK Found', 'maintainability', 'warning',
                 'HACK comment indicates workaround', all_langs,
                 'Replace with proper solution'),

            # Performance
            Rule('HP090', 'String Concatenation', 'performance', 'info',
                 'Inefficient string concatenation',
                 ['python', 'javascript', 'typescript', 'java'],
                 'Use join() or template literals'),
            Rule('HP091', 'Range-based Index Iteration', 'performance', 'info',
                 'Using range(len()) instead of direct iteration', ['python'],
                 'Iterate directly over collection'),
            Rule('HP092', 'Wildcard Import', 'performance', 'info',
                 'Wildcard imports slow startup', ['python'],
                 'Import specific names'),
            Rule('HP093', 'Global Variable Usage', 'performance', 'info',
                 'Global variables impact performance', ['python'],
                 'Use function args or class attributes'),
            Rule('HP094', 'Nested Append in Loop', 'performance', 'info',
                 'May indicate O(n²) complexity', ['python'],
                 'Use list comprehension or itertools'),
            Rule('HP095', 'Hardcoded Sleep', 'performance', 'warning',
                 'Hardcoded sleep duration', ['python'],
                 'Use configurable delays'),
            Rule('HP097', 'File Not Properly Closed', 'performance', 'warning',
                 'File opened without context manager', ['python'],
                 'Use "with open() as f:" pattern'),
            Rule('HP098', 'Array Length in Loop', 'performance', 'info',
                 'Accessing .length in each iteration', ['javascript'],
                 'Cache the length before loop'),
            Rule('HP099', 'Var Declaration', 'performance', 'info',
                 'var has function scope and hoisting', ['javascript'],
                 'Use const or let'),
            Rule('HP100', 'Console Log in Production', 'performance', 'info',
                 'Console.log should be removed in production',
                 ['javascript', 'typescript', 'java'],
                 'Use proper logging library'),
            Rule('HP107', 'Excessive Cloning', 'performance', 'info',
                 'Clone operations can be expensive', ['rust'],
                 'Use references or move semantics'),
            Rule('HP108', 'Unchecked Unwrap', 'performance', 'warning',
                 'unwrap() will panic on None/Err', ['rust'],
                 'Use pattern matching or expect()'),
            Rule('HP109', 'Unnecessary String Constructor', 'performance', 'info',
                 'new String() is unnecessary', ['java'],
                 'Use string literals directly'),
        ]

    @classmethod
    def get_all_rules(cls) -> List[Rule]:
        """Get all registered rules."""
        cls._init_rules()
        return cls._rules

    @classmethod
    def get_rule(cls, rule_id: str) -> Optional[Rule]:
        """Get a specific rule by ID."""
        cls._init_rules()
        for rule in cls._rules:
            if rule.rule_id == rule_id:
                return rule
        return None

    @classmethod
    def get_rules_by_category(cls, category: str) -> List[Rule]:
        """Get rules by category."""
        cls._init_rules()
        return [r for r in cls._rules if r.category == category]

    @classmethod
    def get_rules_by_severity(cls, severity: str) -> List[Rule]:
        """Get rules by severity."""
        cls._init_rules()
        return [r for r in cls._rules if r.severity == severity]
