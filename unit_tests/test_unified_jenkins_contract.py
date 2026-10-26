from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIPELINE = (ROOT / "Jenkinsfile").read_text(encoding="utf-8")


def test_main_jenkinsfile_has_independent_suite_switches():
    for name in (
        "RUN_ALL", "RUN_UNIT", "RUN_PARABANK_SMOKE", "RUN_PARABANK_UI",
        "RUN_PARABANK_API", "RUN_PROCREDIT_DESKTOP_LOGIN",
        "RUN_PROCREDIT_MOBILE_LOGIN", "ALLOW_PROCREDIT_LOGIN",
    ):
        assert f"name: '{name}'" in PIPELINE


def test_live_bank_negative_transfer_is_never_in_unified_jenkinsfile():
    assert 'tests/test_procredit_negative_transfer.py' not in PIPELINE
    assert 'tests/test_procreditbank_mobile_negative_transfer.py' not in PIPELINE
    assert "PRO_CREDIT_NEGATIVE_SUBMIT = 'NO'" in PIPELINE
    assert "PRO_CREDIT_MOBILE_NEGATIVE_SUBMIT = 'NO'" in PIPELINE


def test_junit_and_html_reporting_plugin_are_preserved():
    assert 'reports/*.xml' in PIPELINE
    assert 'reports/html/**/*.html' in PIPELINE
    assert '-m pytest' in PIPELINE
    assert (ROOT / 'reports' / 'pytest_reporting.py').exists()
