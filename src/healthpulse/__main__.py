"""
HealthPulse-CLI - Lightweight Terminal Code Repository Health Diagnosis Engine
轻量级终端代码仓库健康度智能诊断引擎

Usage:
    healthpulse scan <path> [options]
    healthpulse report <path> --format <format>
    healthpulse rules [list|info <rule_id>]
    healthpulse config [show|set <key> <value>]
    healthpulse init [--template <name>]
    healthpulse version

Options:
    -l, --language <lang>     Target language (auto/python/js/ts/go/rust/java)
    -f, --format <format>     Output format (tui/json/html/markdown) [default: tui]
    -o, --output <path>       Output file path
    -r, --rules <rules>       Comma-separated rule IDs to enable (default: all)
    -x, --exclude <patterns>  Comma-separated exclude patterns
    -v, --verbose             Verbose output
    -q, --quiet               Quiet mode, only show score
    --no-color                Disable colored output
    --ci                      CI mode, exit code reflects health score
    --threshold <score>       Minimum health score threshold (0-100) [default: 60]
    -h, --help                Show help
"""

import sys
import os

# Ensure src is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def main():
    """Main entry point for HealthPulse CLI."""
    from healthpulse.cli import HealthPulseCLI

    cli = HealthPulseCLI()
    exit_code = cli.run(sys.argv[1:])
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
