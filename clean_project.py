"""Clean up project cache and temporary files."""

import shutil
import sys
from pathlib import Path


def clean_project(root: Path) -> int:
    """Remove cache directories and temporary files from the project.

    Args:
        root: Project root directory.

    Returns:
        Number of items removed.
    """
    removed = 0

    skip_dirs = {".git", ".venv", "venv", "env", "ENV"}

    cache_dirs = [
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
    ]

    for pattern in cache_dirs:
        for path in root.rglob(pattern):
            if path.is_dir() and not any(part in skip_dirs for part in path.parts):
                shutil.rmtree(path, ignore_errors=True)
                print(f"  removed dir:  {path.relative_to(root)}")
                removed += 1

    temp_patterns = [
        "*.pyc",
        "*.pyo",
        "*.db",
        ".coverage",
        "*.log",
    ]

    for pattern in temp_patterns:
        for path in root.rglob(pattern):
            if path.is_file() and not any(part in skip_dirs for part in path.parts):
                path.unlink(missing_ok=True)
                print(f"  removed file: {path.relative_to(root)}")
                removed += 1

    return removed


def main() -> None:
    """Entry point for the clean command."""
    root = Path(__file__).parent.resolve()
    print(f"Cleaning project: {root.name}")
    count = clean_project(root)
    print(f"Done. {count} item(s) removed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
