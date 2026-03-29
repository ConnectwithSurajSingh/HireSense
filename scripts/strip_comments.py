#!/usr/bin/env python3
"""
Comment Stripping Script for HireSense.

This script removes inline comments from Python files while preserving:
- Module, class, and function docstrings
- Special comments: # noqa, # pragma, # type:, # pylint:, # mypy:
- Shebang lines (#!/...)
- Encoding declarations (# -*- coding: ... -*-)

Usage:
    python scripts/strip_comments.py [--dry-run] [--verbose] [path ...]

Arguments:
    path        Files or directories to process (default: app, testing, utility)
    --dry-run   Show what would be changed without modifying files
    --verbose   Print detailed information about changes

Examples:
    python scripts/strip_comments.py --dry-run
    python scripts/strip_comments.py app/models.py
    python scripts/strip_comments.py --verbose app testing
"""

import argparse
import io
import os
import re
import sys
import tokenize
from pathlib import Path
from typing import List, Set, Tuple


# Patterns for comments that should be preserved
PRESERVED_COMMENT_PATTERNS = [
    r'^#\s*noqa',           # noqa: ignore linting
    r'^#\s*pragma',         # pragma: no cover, etc.
    r'^#\s*type:\s*ignore', # type: ignore
    r'^#\s*pylint:',        # pylint: disable=...
    r'^#\s*mypy:',          # mypy: ignore-errors
    r'^#\s*-\*-',           # -*- coding: utf-8 -*-
    r'^#!',                 # shebang
    r'^#\s*TODO:',          # TODO comments (optional, can remove)
    r'^#\s*FIXME:',         # FIXME comments (optional, can remove)
    r'^#\s*XXX:',           # XXX comments (optional, can remove)
]

PRESERVED_PATTERNS_COMPILED = [re.compile(p, re.IGNORECASE) for p in PRESERVED_COMMENT_PATTERNS]


def should_preserve_comment(comment_text: str) -> bool:
    """
    Check if a comment should be preserved.

    Args:
        comment_text: The comment text including the # symbol.

    Returns:
        True if the comment should be preserved, False otherwise.
    """
    comment_stripped = comment_text.strip()
    for pattern in PRESERVED_PATTERNS_COMPILED:
        if pattern.match(comment_stripped):
            return True
    return False


def strip_comments_from_source(source: str) -> Tuple[str, int]:
    """
    Strip comments from Python source code while preserving docstrings.

    Uses the tokenize module to properly parse Python and identify:
    - COMMENT tokens (inline comments)
    - STRING tokens at specific positions (docstrings)

    Args:
        source: The Python source code as a string.

    Returns:
        A tuple of (modified_source, removed_count).
    """
    try:
        # Tokenize the source
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except tokenize.TokenizeError as e:
        print(f"Warning: Could not tokenize source: {e}")
        return source, 0

    removed_count = 0
    result_tokens = []
    
    for i, token in enumerate(tokens):
        tok_type, tok_string, start, end, line = token
        
        if tok_type == tokenize.COMMENT:
            # Check if this comment should be preserved
            if should_preserve_comment(tok_string):
                result_tokens.append(token)
            else:
                removed_count += 1
                # Skip this comment token
                continue
        else:
            result_tokens.append(token)
    
    # Reconstruct the source from tokens
    try:
        result = tokenize.untokenize(result_tokens)
        # untokenize may add extra spacing, clean it up
        return result, removed_count
    except Exception as e:
        print(f"Warning: Could not reconstruct source: {e}")
        return source, 0


def strip_comments_line_based(source: str) -> Tuple[str, int]:
    """
    Alternative line-based comment stripping for cases where tokenize fails.
    
    This is a fallback method that handles comments on a line-by-line basis.
    It's less accurate but more robust.

    Args:
        source: The Python source code as a string.

    Returns:
        A tuple of (modified_source, removed_count).
    """
    lines = source.splitlines(keepends=True)
    result_lines = []
    removed_count = 0
    in_string = False
    string_char = None
    
    for line in lines:
        # Skip processing if line is part of a multiline string
        stripped = line.lstrip()
        
        # Check for triple-quoted strings (docstrings)
        if '"""' in line or "'''" in line:
            result_lines.append(line)
            continue
        
        # Find comment position (not inside a string)
        comment_pos = -1
        in_str = False
        escape = False
        str_char = None
        
        for j, char in enumerate(line):
            if escape:
                escape = False
                continue
            if char == '\\':
                escape = True
                continue
            if char in '"\'':
                if not in_str:
                    in_str = True
                    str_char = char
                elif char == str_char:
                    in_str = False
                    str_char = None
            elif char == '#' and not in_str:
                comment_pos = j
                break
        
        if comment_pos >= 0:
            comment_text = line[comment_pos:]
            if should_preserve_comment(comment_text):
                result_lines.append(line)
            else:
                # Remove the comment
                new_line = line[:comment_pos].rstrip()
                if new_line or not stripped.startswith('#'):
                    result_lines.append(new_line + '\n' if line.endswith('\n') else new_line)
                else:
                    # Entire line was a comment, skip it
                    pass
                removed_count += 1
        else:
            result_lines.append(line)
    
    return ''.join(result_lines), removed_count


def process_file(filepath: Path, dry_run: bool = False, verbose: bool = False) -> Tuple[bool, int]:
    """
    Process a single Python file to remove comments.

    Args:
        filepath: Path to the Python file.
        dry_run: If True, don't modify the file.
        verbose: If True, print detailed information.

    Returns:
        A tuple of (was_modified, comments_removed).
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False, 0
    
    # Try tokenize-based approach first
    modified, removed_count = strip_comments_from_source(original)
    
    # If tokenize failed or no changes, try line-based approach
    if removed_count == 0 and '#' in original:
        modified, removed_count = strip_comments_line_based(original)
    
    if removed_count == 0:
        if verbose:
            print(f"  {filepath}: No comments to remove")
        return False, 0
    
    if verbose:
        print(f"  {filepath}: {removed_count} comment(s) removed")
    
    if not dry_run:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(modified)
        except Exception as e:
            print(f"Error writing {filepath}: {e}")
            return False, 0
    
    return True, removed_count


def find_python_files(paths: List[str]) -> List[Path]:
    """
    Find all Python files in the given paths.

    Args:
        paths: List of file or directory paths.

    Returns:
        List of Path objects for Python files.
    """
    python_files = []
    
    for path_str in paths:
        path = Path(path_str)
        if path.is_file() and path.suffix == '.py':
            python_files.append(path)
        elif path.is_dir():
            python_files.extend(path.rglob('*.py'))
    
    return sorted(set(python_files))


def main():
    """Main entry point for the comment stripping script."""
    parser = argparse.ArgumentParser(
        description='Strip comments from Python files while preserving docstrings.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        'paths',
        nargs='*',
        default=['app', 'testing', 'utility'],
        help='Files or directories to process (default: app, testing, utility)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Print detailed information about changes'
    )
    
    args = parser.parse_args()
    
    # Change to project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    print(f"Comment Stripping Script")
    print(f"{'=' * 40}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"Paths: {', '.join(args.paths)}")
    print()
    
    python_files = find_python_files(args.paths)
    
    if not python_files:
        print("No Python files found.")
        return 0
    
    print(f"Found {len(python_files)} Python file(s)")
    print()
    
    total_modified = 0
    total_comments_removed = 0
    
    for filepath in python_files:
        was_modified, comments_removed = process_file(
            filepath, 
            dry_run=args.dry_run, 
            verbose=args.verbose
        )
        if was_modified:
            total_modified += 1
            total_comments_removed += comments_removed
    
    print()
    print(f"{'=' * 40}")
    print(f"Summary:")
    print(f"  Files processed: {len(python_files)}")
    print(f"  Files modified: {total_modified}")
    print(f"  Comments removed: {total_comments_removed}")
    
    if args.dry_run and total_modified > 0:
        print()
        print("This was a dry run. No files were modified.")
        print("Run without --dry-run to apply changes.")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
