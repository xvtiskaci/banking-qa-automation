"""Offline checks for per-test HTML reporting, logging and screenshot links."""

from datetime import datetime

from utils.TestReport import _redact, save_test_report


def test_html_report_and_log_entries(tmp_path):
    html_file = save_test_report(
        test_name="test_login",
        nodeid="tests/test_procredit_login.py::TestLogin::test_login",
        status="PASSED",
        started_at=datetime(2026, 10, 26, 11, 31, 42, 123456),
        duration_seconds=1.256,
        logs=["11:31:42 | INFO | Finding element: Login",
              "11:31:43 | INFO | Clicking element: Sign in"],
        output_dir=tmp_path,
    )
    assert html_file.parent == tmp_path / "html"
    assert html_file.name == "test_login_2026-10-26_11-31-42_123456.html"
    rendered = html_file.read_text(encoding="utf-8")
    assert "Finding element: Login" in rendered
    assert "Clicking element: Sign in" in rendered
    assert "PASSED" in rendered
    assert not (tmp_path / "pdf").exists()
    assert not list(tmp_path.rglob("*.pdf"))


def test_failed_report_links_screenshot_and_escapes_log_html(tmp_path):
    screenshot = tmp_path / "screenshots" / "NoSuchElementException_test_login_abc.png"
    screenshot.parent.mkdir(parents=True)
    screenshot.write_bytes(b"test-placeholder")
    html_file = save_test_report(
        test_name="test_login[secret_param]",
        nodeid="tests/test_procredit_login.py::test_login",
        status="FAILED",
        started_at=datetime(2026, 10, 26, 11, 33, 0),
        duration_seconds=0.21,
        logs=["11:33:00 | INFO | Checking <button>"],
        exception_name="NoSuchElementException",
        screenshot_path=screenshot,
        output_dir=tmp_path,
    )
    content = html_file.read_text(encoding="utf-8")
    assert "NoSuchElementException" in content
    assert "../screenshots/NoSuchElementException_test_login_abc.png" in content
    assert "&lt;button&gt;" in content
    assert "<button>" not in content
    assert "secret_param" not in html_file.name
    assert not (tmp_path / "pdf").exists()


def test_redacts_known_secret_from_logs(monkeypatch):
    monkeypatch.setenv("PRO_CREDIT_PASSWORD", "BankPasswordSuperSecret")
    line = "password=abcdef PRO_CREDIT_PASSWORD=BankPasswordSuperSecret"
    value = _redact(line)
    assert "BankPasswordSuperSecret" not in value
    assert "password=[REDACTED]" in value


def test_skipped_report_without_actions(tmp_path):
    html_file = save_test_report(
        test_name="test_skipped",
        nodeid="api_tests/test_demo.py::test_skipped",
        status="SKIPPED",
        started_at=datetime(2026, 10, 26, 11, 34, 0),
        duration_seconds=0.0,
        logs=[],
        output_dir=tmp_path,
    )
    assert "No LoggerUtils actions" in html_file.read_text(encoding="utf-8")
    assert not (tmp_path / "pdf").exists()


def test_project_reporting_plugin_is_loaded(pytestconfig):
    assert pytestconfig.pluginmanager.hasplugin("reports.pytest_reporting"), (
        "Enable the reporting plugin in pytest.ini so PyCharm and Jenkins write HTML reports"
    )
