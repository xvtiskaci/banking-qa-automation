"""Screenshot helper tests: no browser or external account required."""

from pathlib import Path

from utils.FailureScreenshot import SCREENSHOTS_DIR, save_failure_screenshot


class FakeDriver:
    def __init__(self, successful=True):
        self.successful = successful

    def save_screenshot(self, filename):
        if not self.successful:
            return False
        Path(filename).write_bytes(b"not a real png; unit-test placeholder")
        return True


def test_saves_exception_test_name_and_png(tmp_path):
    file = save_failure_screenshot(
        FakeDriver(), "NoSuchElementException", "test_procredit_login", tmp_path
    )
    assert file.parent == tmp_path
    assert file.name.startswith("NoSuchElementException_test_procredit_login_")
    assert file.suffix == ".png"
    assert file.exists()


def test_repeated_failures_generate_distinct_files(tmp_path):
    first = save_failure_screenshot(FakeDriver(), "TimeoutException", "test_login", tmp_path)
    second = save_failure_screenshot(FakeDriver(), "TimeoutException", "test_login", tmp_path)
    assert first != second
    assert first.is_file() and second.is_file()


def test_filename_excludes_error_message_and_unsafe_characters(tmp_path):
    file = save_failure_screenshot(
        FakeDriver(), "AssertionError", "test_login[/\\:secret]", tmp_path
    )
    assert file.name.startswith("AssertionError_test_login_secret_")
    assert not any(char in file.name for char in ("/", "\\", ":", "[", "]"))


def test_default_screenshots_folder_is_under_reports():
    assert SCREENSHOTS_DIR.parts[-2:] == ("reports", "screenshots")
