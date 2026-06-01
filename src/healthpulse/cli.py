"""
HealthPulse CLI - Command-line interface for code health diagnosis.
"""

import sys
import os
import argparse
import json
import time
from pathlib import Path

from healthpulse import __version__
from healthpulse.scanner import RepositoryScanner
from healthpulse.engine import DiagnosisEngine
from healthpulse.reporters.tui_reporter import TUIReporter
from healthpulse.reporters.json_reporter import JSONReporter
from healthpulse.reporters.html_reporter import HTMLReporter
from healthpulse.reporters.markdown_reporter import MarkdownReporter
from healthpulse.utils.color import Color
from healthpulse.utils.config import Config


class HealthPulseCLI:
    """Main CLI handler for HealthPulse."""

    def __init__(self):
        self.config = Config()
        self.color = Color()

    def run(self, args=None):
        """Execute CLI command."""
        if args is None:
            args = sys.argv[1:]

        if not args or args[0] in ('-h', '--help', 'help'):
            self._show_help()
            return 0

        if args[0] in ('-v', '--version', 'version'):
            self._show_version()
            return 0

        command = args[0]
        remaining = args[1:]

        handlers = {
            'scan': self._cmd_scan,
            'report': self._cmd_report,
            'rules': self._cmd_rules,
            'config': self._cmd_config,
            'init': self._cmd_init,
        }

        handler = handlers.get(command)
        if handler is None:
            print(f"{self.color.red('Error:')} Unknown command '{command}'")
            print(f"Run 'healthpulse help' for available commands.")
            return 1

        try:
            return handler(remaining)
        except KeyboardInterrupt:
            print(f"\n{self.color.yellow('Interrupted.')}")
            return 130
        except Exception as e:
            print(f"{self.color.red(f'Error: {e}')}")
            if os.environ.get('HEALTHPULSE_DEBUG'):
                import traceback
                traceback.print_exc()
            return 1

    def _show_help(self):
        """Display help information."""
        help_text = f"""
{self.color.cyan('╔══════════════════════════════════════════════════════════════╗')}
{self.color.cyan('║')}  {self.color.bold_white('HealthPulse-CLI')}  v{__version__}                              {self.color.cyan('║')}
{self.color.cyan('║')}  {self.color.dim('Lightweight Code Repository Health Diagnosis Engine')}           {self.color.cyan('║')}
{self.color.cyan('╚══════════════════════════════════════════════════════════════╝')}

{self.color.bold('USAGE:')}
  healthpulse <command> [options] [arguments]

{self.color.bold('COMMANDS:')}
  {self.color.green('scan')}     <path>       Scan a code repository and diagnose health
  {self.color.green('report')}   <path>       Generate a detailed health report
  {self.color.green('rules')}    [list|info]  List or inspect available rules
  {self.color.green('config')}   [show|set]   View or modify configuration
  {self.color.green('init')}                  Initialize a new HealthPulse config

{self.color.bold('SCAN OPTIONS:')}
  -l, --language <lang>      Target language (auto/python/js/ts/go/rust/java)
  -f, --format <format>      Output format (tui/json/html/markdown)
  -o, --output <path>        Save output to file
  -r, --rules <rules>        Enable specific rules (comma-separated)
  -x, --exclude <patterns>   Exclude patterns (comma-separated)
  -v, --verbose              Show verbose output
  -q, --quiet                Only show health score
  --no-color                 Disable colors
  --ci                       CI mode (exit code = health status)
  --threshold <score>        Min health score (default: 60)

{self.color.bold('EXAMPLES:')}
  {self.color.dim('$ healthpulse scan ./my-project')}
  {self.color.dim('$ healthpulse scan ./src --language python --format json -o report.json')}
  {self.color.dim('$ healthpulse scan . --ci --threshold 70')}
  {self.color.dim('$ healthpulse report ./my-project --format html -o health.html')}
  {self.color.dim('$ healthpulse rules list')}
  {self.color.dim('$ healthpulse rules info HP001')}

{self.color.bold('DIMENSIONS (8):')}
  {self.color.yellow('■')} Complexity    {self.color.yellow('■')} Duplication   {self.color.yellow('■')} Naming
  {self.color.yellow('■')} Security      {self.color.yellow('■')} Architecture   {self.color.yellow('■')} Documentation
  {self.color.yellow('■')} Maintainability {self.color.yellow('■')} Performance

{self.color.dim(f'Powered by GLM-5.1 | MIT License | {len(self._get_all_rules())} rules')}
"""
        print(help_text)

    def _show_version(self):
        """Display version info."""
        print(f"HealthPulse-CLI v{__version__}")
        print(f"Python {sys.version.split()[0]}")

    def _get_all_rules(self):
        """Get all available rules."""
        try:
            from healthpulse.rules.registry import RuleRegistry
            return RuleRegistry.get_all_rules()
        except Exception:
            return []

    def _parse_scan_args(self, args):
        """Parse scan/report command arguments."""
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('path', nargs='?', default='.')
        parser.add_argument('-l', '--language', default='auto')
        parser.add_argument('-f', '--format', default='tui')
        parser.add_argument('-o', '--output', default=None)
        parser.add_argument('-r', '--rules', default=None)
        parser.add_argument('-x', '--exclude', default=None)
        parser.add_argument('-v', '--verbose', action='store_true')
        parser.add_argument('-q', '--quiet', action='store_true')
        parser.add_argument('--no-color', action='store_true')
        parser.add_argument('--ci', action='store_true')
        parser.add_argument('--threshold', type=int, default=60)
        return parser.parse_args(args)

    def _cmd_scan(self, args):
        """Execute scan command."""
        opts = self._parse_scan_args(args)

        if opts.no_color:
            self.color.disable()

        target_path = Path(opts.path).resolve()
        if not target_path.exists():
            print(f"{self.color.red('Error:')} Path '{opts.path}' does not exist.")
            return 1

        if not opts.quiet:
            print(f"\n{self.color.cyan('🩺 HealthPulse-CLI')} v{__version__}")
            print(f"{self.color.dim('━' * 55)}")
            print(f"  Target:  {self.color.white(target_path)}")
            print(f"  Language: {self.color.white(opts.language)}")
            print(f"  Format:   {self.color.white(opts.format)}")
            print(f"{self.color.dim('━' * 55)}\n")

        start_time = time.time()

        # Phase 1: Scan repository
        if not opts.quiet:
            print(f"  {self.color.yellow('⏳')} Scanning repository...")

        scanner = RepositoryScanner(
            root_path=target_path,
            language=opts.language,
            exclude_patterns=opts.exclude,
            verbose=opts.verbose,
        )
        scan_result = scanner.scan()

        if not opts.quiet:
            print(f"  {self.color.green('✓')} Found {self.color.white(str(scan_result.total_files))} files"
                  f" ({self.color.white(str(scan_result.total_lines))} lines)")
            print(f"  {self.color.yellow('⏳')} Running diagnosis ({len(scan_result.files)} files)...")

        # Phase 2: Run diagnosis
        engine = DiagnosisEngine(
            rules_filter=opts.rules,
            verbose=opts.verbose,
        )
        diagnosis = engine.diagnose(scan_result)

        elapsed = time.time() - start_time

        # Phase 3: Generate report
        if not opts.quiet:
            print(f"  {self.color.green('✓')} Diagnosis complete ({self.color.white(f'{elapsed:.2f}s')})")
            print()

        reporters = {
            'tui': TUIReporter,
            'json': JSONReporter,
            'html': HTMLReporter,
            'markdown': MarkdownReporter,
        }

        reporter_cls = reporters.get(opts.format)
        if reporter_cls is None:
            print(f"{self.color.red('Error:')} Unknown format '{opts.format}'. "
                  f"Available: {', '.join(reporters.keys())}")
            return 1

        reporter = reporter_cls(color=self.color if opts.format == 'tui' else None)
        report = reporter.generate(diagnosis)

        if opts.output:
            output_path = Path(opts.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report, encoding='utf-8')
            if not opts.quiet:
                print(f"  {self.color.green('📄')} Report saved to {self.color.white(str(output_path))}")
        else:
            print(report)

        # CI mode: exit code reflects health
        if opts.ci:
            score = diagnosis.overall_score
            if score < opts.threshold:
                print(f"\n{self.color.red(f'✗ Health score {score} < threshold {opts.threshold}')}")
                return 2
            print(f"\n{self.color.green(f'✓ Health score {score} >= threshold {opts.threshold}')}")
            return 0

        return 0

    def _cmd_report(self, args):
        """Execute report command - alias for scan with format."""
        return self._cmd_scan(args)

    def _cmd_rules(self, args):
        """Execute rules command."""
        from healthpulse.rules.registry import RuleRegistry

        if not args or args[0] == 'list':
            rules = RuleRegistry.get_all_rules()
            print(f"\n{self.color.cyan('📋 Available Rules')} ({len(rules)} total)\n")
            print(f"  {'ID':<8} {'Severity':<10} {'Category':<18} {'Name'}")
            print(f"  {'─' * 8} {'─' * 10} {'─' * 18} {'─' * 30}")
            for rule in sorted(rules, key=lambda r: r.rule_id):
                sev_color = {
                    'critical': self.color.red,
                    'warning': self.color.yellow,
                    'info': self.color.blue,
                    'hint': self.color.dim,
                }.get(rule.severity, self.color.white)
                print(f"  {rule.rule_id:<8} {sev_color(rule.severity):<10} "
                      f"{self.color.dim(rule.category):<18} {rule.name}")
            return 0

        if args[0] == 'info' and len(args) > 1:
            rule_id = args[1]
            rule = RuleRegistry.get_rule(rule_id)
            if rule is None:
                print(f"{self.color.red('Error:')} Rule '{rule_id}' not found.")
                return 1
            print(f"\n{self.color.cyan(f'📋 Rule: {rule.rule_id} - {rule.name}')}")
            print(f"  Category:  {rule.category}")
            print(f"  Severity:  {rule.severity}")
            print(f"  Languages: {', '.join(rule.languages)}")
            print(f"\n  {self.color.white(rule.description)}")
            return 0

        print(f"{self.color.red('Error:')} Invalid rules command. Use 'list' or 'info <rule_id>'.")
        return 1

    def _cmd_config(self, args):
        """Execute config command."""
        if not args or args[0] == 'show':
            cfg = self.config.load()
            print(f"\n{self.color.cyan('⚙️  HealthPulse Configuration')}\n")
            for key, value in cfg.items():
                print(f"  {self.color.white(key)}: {self.color.dim(str(value))}")
            return 0

        if args[0] == 'set' and len(args) >= 3:
            key, value = args[1], args[2]
            self.config.set(key, value)
            self.config.save()
            print(f"{self.color.green('✓')} Config updated: {key} = {value}")
            return 0

        print(f"{self.color.red('Error:')} Invalid config command. Use 'show' or 'set <key> <value>'.")
        return 1

    def _cmd_init(self, args):
        """Initialize HealthPulse config in current directory."""
        config_path = Path.cwd() / '.healthpulse.json'
        if config_path.exists():
            print(f"{self.color.yellow('⚠')} .healthpulse.json already exists.")
            return 1

        default_config = {
            "version": "1.0",
            "language": "auto",
            "threshold": 60,
            "exclude": [
                "node_modules",
                ".git",
                "__pycache__",
                ".venv",
                "venv",
                "dist",
                "build",
                ".next",
                ".cache",
                "coverage",
            ],
            "rules": {
                "enabled": "all",
                "disabled": [],
            },
            "dimensions": {
                "complexity": {"weight": 1.0},
                "duplication": {"weight": 1.0},
                "naming": {"weight": 0.8},
                "security": {"weight": 1.2},
                "architecture": {"weight": 0.9},
                "documentation": {"weight": 0.7},
                "maintainability": {"weight": 1.0},
                "performance": {"weight": 0.8},
            },
            "ci": {
                "enabled": false,
                "threshold": 60,
            },
        }

        config_path.write_text(json.dumps(default_config, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"{self.color.green('✓')} Created {self.color.white('.healthpulse.json')}")
        print(f"  Run {self.color.dim('healthpulse scan .')} to start diagnosis.")
        return 0
