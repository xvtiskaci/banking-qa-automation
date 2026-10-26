
from datetime import datetime
from pathlib import Path
import re


SCREENSHOTS_DIR = Path(__file__).resolve().parents[1] / "reports" / "screenshots"


def _safe_filename_part(value: str, limit: int) -> str:
    part = re.sub(r"[^A-Za-z0-9_-]+", "_", str(value)).strip("_")
    return (part or "Unknown")[:limit]


def save_failure_screenshot(
    driver,
    error_name: str,
    test_name: str,
    output_dir: Path | None = None,
) -> Path:
    directory = Path(output_dir) if output_dir is not None else SCREENSHOTS_DIR
    directory.mkdir(parents=True, exist_ok=True)

    error = _safe_filename_part(error_name, 70)
    test = _safe_filename_part(test_name, 90)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    path = directory / f"{error}_{test}_{timestamp}.png"

    if driver.save_screenshot(str(path)) is False or not path.is_file():
        raise RuntimeError("Browser did not save a screenshot")
    return path
