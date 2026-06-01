"""
Color utility - Terminal color formatting.
"""

import os
import sys


class Color:
    """Terminal color formatting utility."""

    COLORS = {
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'bright_black': '\033[90m',
        'bright_red': '\033[91m',
        'bright_green': '\033[92m',
        'bright_yellow': '\033[93m',
        'bright_blue': '\033[94m',
        'bright_magenta': '\033[95m',
        'bright_cyan': '\033[96m',
        'bright_white': '\033[97m',
    }

    STYLES = {
        'bold': '\033[1m',
        'dim': '\033[2m',
        'underline': '\033[4m',
        'reset': '\033[0m',
    }

    def __init__(self):
        self._enabled = self._detect_color_support()

    def _detect_color_support(self) -> bool:
        """Detect if terminal supports colors."""
        if os.environ.get('NO_COLOR'):
            return False
        if os.environ.get('HEALTHPULSE_NO_COLOR'):
            return False
        if not sys.stdout.isatty():
            return False
        if os.environ.get('TERM') in ('dumb', ''):
            return False
        return True

    def disable(self):
        """Disable color output."""
        self._enabled = False

    def _wrap(self, text: str, *codes: str) -> str:
        """Wrap text with color/style codes."""
        if not self._enabled:
            return text
        return ''.join(codes) + text + self.STYLES['reset']

    def __getattr__(self, name: str):
        """Dynamic color method access."""
        if name in self.COLORS:
            return lambda text: self._wrap(text, self.COLORS[name])
        if name in self.STYLES:
            return lambda text: self._wrap(text, self.STYLES[name])
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")

    def bold_white(self, text: str) -> str:
        return self._wrap(text, self.STYLES['bold'], self.COLORS['white'])

    def bold_red(self, text: str) -> str:
        return self._wrap(text, self.STYLES['bold'], self.COLORS['red'])

    def bold_green(self, text: str) -> str:
        return self._wrap(text, self.STYLES['bold'], self.COLORS['green'])

    def bold_yellow(self, text: str) -> str:
        return self._wrap(text, self.STYLES['bold'], self.COLORS['yellow'])

    def bold_blue(self, text: str) -> str:
        return self._wrap(text, self.STYLES['bold'], self.COLORS['blue'])

    def bold_cyan(self, text: str) -> str:
        return self._wrap(text, self.STYLES['bold'], self.COLORS['cyan'])

    def dim(self, text: str) -> str:
        return self._wrap(text, self.STYLES['dim'])

    def score_color(self, score: float) -> str:
        """Return color based on score value."""
        if score >= 80:
            return self.bold_green(str(score))
        elif score >= 60:
            return self.bold_yellow(str(score))
        elif score >= 40:
            return str(score)
        else:
            return self.bold_red(str(score))

    def grade_color(self, grade: str) -> str:
        """Return color based on grade."""
        if grade.startswith('A'):
            return self.bold_green(grade)
        elif grade.startswith('B'):
            return self.bold_yellow(grade)
        elif grade.startswith('C'):
            return str(grade)
        else:
            return self.bold_red(grade)

    def severity_color(self, severity: str) -> str:
        """Return color based on severity."""
        colors = {
            'critical': self.bold_red,
            'warning': self.bold_yellow,
            'info': self.blue,
            'hint': self.dim,
        }
        fn = colors.get(severity, lambda x: x)
        return fn(severity.upper())

    def bar(self, value: float, width: int = 20) -> str:
        """Generate a colored progress bar."""
        filled = int(width * value / 100)
        empty = width - filled

        if value >= 80:
            bar_color = self.COLORS['green']
        elif value >= 60:
            bar_color = self.COLORS['yellow']
        elif value >= 40:
            bar_color = self.COLORS['blue']
        else:
            bar_color = self.COLORS['red']

        if self._enabled:
            return f"{bar_color}{'█' * filled}{self.STYLES['dim']}{'░' * empty}{self.STYLES['reset']}"
        return f"{'#' * filled}{'-' * empty}"
