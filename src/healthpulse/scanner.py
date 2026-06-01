"""
Repository Scanner - Walks through code repositories and collects file data.
"""

import os
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict


# Language detection by file extension
LANGUAGE_MAP = {
    '.py': 'python',
    '.pyw': 'python',
    '.js': 'javascript',
    '.jsx': 'javascript',
    '.ts': 'typescript',
    '.tsx': 'typescript',
    '.mjs': 'javascript',
    '.cjs': 'javascript',
    '.go': 'go',
    '.rs': 'rust',
    '.java': 'java',
    '.kt': 'kotlin',
    '.rb': 'ruby',
    '.php': 'php',
    '.cs': 'csharp',
    '.cpp': 'cpp',
    '.c': 'c',
    '.h': 'c',
    '.hpp': 'cpp',
    '.swift': 'swift',
    '.scala': 'scala',
    '.r': 'r',
    '.lua': 'lua',
    '.sh': 'shell',
    '.bash': 'shell',
    '.zsh': 'shell',
    '.ps1': 'powershell',
    '.sql': 'sql',
    '.vue': 'vue',
    '.svelte': 'svelte',
}

# Default exclude patterns
DEFAULT_EXCLUDES = {
    'node_modules', '.git', '__pycache__', '.venv', 'venv',
    'dist', 'build', '.next', '.cache', 'coverage', '.tox',
    '.mypy_cache', '.pytest_cache', '.eggs', '*.egg-info',
    '.idea', '.vscode', 'vendor', 'Pods', '.gradle',
    'target', 'bin', 'obj', 'out', '.turbo', '.nuxt',
}

# Binary file extensions to skip
BINARY_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg',
    '.mp3', '.mp4', '.avi', '.mov', '.wav', '.flac',
    '.zip', '.tar', '.gz', '.rar', '.7z', '.bz2',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.exe', '.dll', '.so', '.dylib', '.bin', '.wasm',
    '.ttf', '.otf', '.woff', '.woff2', '.eot',
    '.pyc', '.pyo', '.class', '.o', '.obj',
}


@dataclass
class FileInfo:
    """Represents a single source file."""
    path: Path
    language: str
    lines: List[str]
    line_count: int
    size_bytes: int

    @property
    def filename(self) -> str:
        return self.path.name

    @property
    def extension(self) -> str:
        return self.path.suffix.lower()

    @property
    def relative_path(self) -> str:
        return str(self.path)


@dataclass
class ScanResult:
    """Result of a repository scan."""
    root_path: Path
    files: List[FileInfo] = field(default_factory=list)
    total_files: int = 0
    total_lines: int = 0
    total_size: int = 0
    languages: Dict[str, int] = field(default_factory=dict)
    scan_time: float = 0.0

    @property
    def primary_language(self) -> Optional[str]:
        """Return the most common language."""
        if not self.languages:
            return None
        return max(self.languages, key=self.languages.get)


class RepositoryScanner:
    """Scans a code repository and collects file information."""

    def __init__(self, root_path: Path, language: str = 'auto',
                 exclude_patterns: Optional[str] = None,
                 verbose: bool = False):
        self.root_path = root_path
        self.language_filter = language
        self.verbose = verbose
        self.exclude_patterns = self._parse_excludes(exclude_patterns)

    def _parse_excludes(self, patterns_str: Optional[str]) -> set:
        """Parse exclude patterns from string."""
        excludes = DEFAULT_EXCLUDES.copy()
        if patterns_str:
            for p in patterns_str.split(','):
                p = p.strip()
                if p:
                    excludes.add(p)
        return excludes

    def _should_exclude(self, path: Path) -> bool:
        """Check if a path should be excluded."""
        parts = path.parts
        for part in parts:
            if part in self.exclude_patterns:
                return True
        # Check glob patterns
        name = path.name
        for pattern in self.exclude_patterns:
            if pattern.startswith('*') and name.endswith(pattern[1:]):
                return True
            if pattern.startswith('.') and name == pattern:
                return True
        return False

    def _detect_language(self, path: Path) -> Optional[str]:
        """Detect programming language from file extension."""
        ext = path.suffix.lower()
        return LANGUAGE_MAP.get(ext)

    def _is_binary(self, path: Path) -> bool:
        """Check if a file is binary."""
        return path.suffix.lower() in BINARY_EXTENSIONS

    def _read_file_safe(self, path: Path) -> Optional[List[str]]:
        """Safely read file contents."""
        try:
            # Try UTF-8 first
            content = path.read_text(encoding='utf-8')
            return content.splitlines()
        except UnicodeDecodeError:
            try:
                content = path.read_text(encoding='latin-1')
                return content.splitlines()
            except Exception:
                return None
        except Exception:
            return None

    def scan(self) -> ScanResult:
        """Scan the repository and collect file data."""
        import time
        start_time = time.time()

        result = ScanResult(root_path=self.root_path)

        if not self.root_path.is_dir():
            # Single file scan
            file_info = self._scan_file(self.root_path)
            if file_info:
                result.files.append(file_info)
                result.total_files = 1
                result.total_lines = file_info.line_count
                result.total_size = file_info.size_bytes
                result.languages[file_info.language] = 1
            result.scan_time = time.time() - start_time
            return result

        # Walk directory tree
        for root, dirs, files in os.walk(self.root_path):
            root_path = Path(root)

            # Filter excluded directories in-place
            dirs[:] = [d for d in dirs if not self._should_exclude(root_path / d)]

            for filename in sorted(files):
                file_path = root_path / filename

                if self._should_exclude(file_path):
                    continue
                if self._is_binary(file_path):
                    continue

                lang = self._detect_language(file_path)
                if lang is None:
                    continue

                # Language filter
                if self.language_filter != 'auto' and lang != self.language_filter:
                    continue

                file_info = self._scan_file(file_path, lang)
                if file_info:
                    result.files.append(file_info)
                    result.total_files += 1
                    result.total_lines += file_info.line_count
                    result.total_size += file_info.size_bytes
                    result.languages[lang] = result.languages.get(lang, 0) + 1

        result.scan_time = time.time() - start_time
        return result

    def _scan_file(self, path: Path, language: str = None) -> Optional[FileInfo]:
        """Scan a single file."""
        if language is None:
            language = self._detect_language(path)
            if language is None:
                return None

        lines = self._read_file_safe(path)
        if lines is None:
            return None

        try:
            size = path.stat().st_size
        except OSError:
            size = 0

        return FileInfo(
            path=path,
            language=language,
            lines=lines,
            line_count=len(lines),
            size_bytes=size,
        )
