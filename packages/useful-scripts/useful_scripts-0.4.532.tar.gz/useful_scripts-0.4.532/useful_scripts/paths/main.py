import logging
from pathlib import Path


def path_check(file_path: Path | str) -> Path | None:
    """Make sure file_path is a valid Path object. If failed, return None."""
    if isinstance(file_path, str):
        file_path = Path(file_path)

    if isinstance(file_path, Path):
        # make sure dir exists
        if not file_path.name.startswith('.') and not file_path.suffix:
            file_path.mkdir(parents=True, exist_ok=True)

        if file_path.exists():
            return file_path
    logging.warning(f"file_path: {file_path} is not a valid.")
    return None
