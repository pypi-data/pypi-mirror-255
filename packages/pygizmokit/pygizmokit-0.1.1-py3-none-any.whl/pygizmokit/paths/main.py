import logging
from pathlib import Path


def path_check(file_path: Path | str) -> Path | None:
    """Make sure file_path is a valid Path object. If failed, return None."""
    if isinstance(file_path, str):
        file_path = Path(file_path)

    if isinstance(file_path, Path) and file_path.exists():
        return file_path
    logging.warning(f"file_path: {file_path} is not a valid.")
    return None
