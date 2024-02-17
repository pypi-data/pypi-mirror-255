"""
This module cleans the project build files and caches
"""

import shutil
from pathlib import Path
from typing import Generator

ITEMS_TO_CLEAN = dict(
    build_dir=Path("./build/"),
    dist_dir=Path("./dist/"),
    egg_info=Path().rglob("*.egg-info/"),
    log_files=Path().rglob("*.log"),
    py_caches=Path().rglob("__pycache__/"),
)


def delete(path: Path):
    if not path.exists():
        return
    if path.is_dir():
        print(f"Deleting directory: {path}")
        shutil.rmtree(path)
    else:
        print(f"Deleting file: {path}")
        path.unlink()


def main():
    for item in ITEMS_TO_CLEAN.values():
        # Handle Globs
        if isinstance(item, Generator):
            for sub_item in item:
                delete(sub_item)
        # Handle Single Paths
        if isinstance(item, Path):
            delete(item)


if __name__ == "__main__":
    main()
