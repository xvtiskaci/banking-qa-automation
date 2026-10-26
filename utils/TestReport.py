"""Standalone HTML reports for individual pytest cases (no browser required)."""

from __future__ import annotations

import html
import os
import re
from datetime import datetime
from pathlib import Path

REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports"

# Only redact values for known secrets: never blank every short number in a log.
_SECRET_ENV_KEYS = (
    "PRO_CREDIT_PASSWORD", "PARABANK_PASSWORD", "API_TOKEN", "ACCESS_TOKEN",
    "SECRET_KEY", "AUTH_TOKEN", "OTP_CODE", "TAN_CODE",
)


def _redact(value: str) -> str:
    text = str(value)
    for key in _SECRET_ENV_KEYS:
        secret = os.environ.get(key)
        if secret and len(secret) >= 4:
            text = text.replace(secret, "[REDACTED]")
    text = re.sub(r"(?i)(\b(?:password|token|otp|tan|authorization|secret)\s*[:=]\s*)([^\s,;]+)",
                  r"\1[REDACTED]", text)
    return text


def _safe_test_filename(test_name: str) -> str:
    test_name = test_name.split("[", 1)[0]
    return (re.sub(r"[^A-Za-z0-9_-]+", "_", test_name).strip("_") or "test")[:100]


def _write_html(path: Path, details: dict, logs: Iterable[str], screenshot: Path | None):
    status = details["Status"]
    status_class = {"PASSED": "passed", "FAILED": "failed", "SKIPPED": "skipped"}.get(status, "skipped")
    metadata = "\n".join(
        f"<dt>{html.escape(k)}</dt><dd>{html.escape(str(v))}</dd>"
        for k, v in details.items() if k != "Screenshot" and v
    )
    lines = list(logs)
    log_entries = "\n".join(
        f"<div class='log-row'>{html.escape(_redact(line))}</div>" for line in lines
    ) or "<p class='muted'>No LoggerUtils actions were recorded for this test.</p>"
    link = ""
    if screenshot is not None and screenshot.is_file():
        # Only use a basename so no local machine path is accidentally disclosed.
        relative = "../screenshots/" + screenshot.name
        link = f'<a class="screenshot" href="{html.escape(relative, quote=True)}">View failure screenshot (PNG)</a>'
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(details['Test'])} - {html.escape(status)}</title>
<style>
:root{{font-family:Segoe UI,Arial,sans-serif;color:#15243a;background:#f4f7fb}}
body{{max-width:1020px;margin:32px auto;padding:0 20px}}
main{{background:white;border:1px solid #e4e9f0;border-radius:14px;padding:30px;box-shadow:0 8px 24px #1b365517}}
h1{{font-size:26px;margin:0 0 16px}}
.status{{display:inline-block;padding:7px 13px;border-radius:99px;font-weight:700}}
.passed{{color:#17653e;background:#dcfce7}}.failed{{color:#991b1b;background:#fee2e2}}.skipped{{color:#7c5300;background:#fef3c7}}
dl{{display:grid;grid-template-columns:150px minmax(0,1fr);gap:9px;margin:22px 0 26px}}dt{{color:#627086}}dd{{margin:0;overflow-wrap:anywhere}}
section{{border-top:1px solid #e4e9f0;padding-top:18px}}
h2{{font-size:18px}}.logs{{border-radius:10px;background:#0e1726;color:#e7effc;padding:17px;overflow-wrap:anywhere}}
.log-row{{white-space:pre-wrap;line-height:1.5;font:13px/1.5 Consolas,'Courier New',monospace;padding:3px 0;border-bottom:1px solid #29384b}}
.muted{{color:#798aa1}}.screenshot{{display:inline-block;margin-bottom:18px;color:#1566a9}}
@media print{{body{{margin:0;max-width:none;background:white}}main{{border:0;box-shadow:none;padding:10px}}.logs{{background:white;color:black}}.log-row{{border-color:#ddd}}}}
</style></head><body><main>
<h1>Automation test report</h1><span class="status {status_class}">{html.escape(status)}</span>
<dl>{metadata}</dl>{link}
<section><h2>Execution logs</h2><div class="logs">{log_entries}</div></section>
</main></body></html>"""
    path.write_text(document, encoding="utf-8")


def save_test_report(*, test_name: str, nodeid: str, status: str,
                     started_at: datetime, duration_seconds: float,
                     logs: list[str], exception_name: str | None = None,
                     screenshot_path: Path | None = None,
                     output_dir: Path | None = None) -> Path:
    root = Path(output_dir) if output_dir is not None else REPORTS_DIR
    html_dir = root / "html"
    html_dir.mkdir(parents=True, exist_ok=True)
    stamp = started_at.strftime("%Y-%m-%d_%H-%M-%S_%f")
    stem = f"{_safe_test_filename(test_name)}_{stamp}"
    html_path = html_dir / f"{stem}.html"
    details = {
        "Test": _redact(nodeid),
        "Status": status,
        "Date and time": started_at.strftime("%Y-%m-%d %H:%M:%S"),
        "Duration": f"{duration_seconds:.3f} seconds",
        "Error": exception_name or "-",
        "Screenshot": screenshot_path.name if screenshot_path else "-",
    }
    _write_html(html_path, details, logs, screenshot_path)
    return html_path
