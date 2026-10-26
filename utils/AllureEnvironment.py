import os
import platform
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


def _package_version(package_name):
    try:
        return version(package_name)
    except PackageNotFoundError:
        return "not installed"


def _clean(value):
    return str(value).replace("\\", "/").replace("\r", " ").replace("\n", " ").strip()


def write_allure_environment(results_dir, browser_name=None, browser_version=None):
    if not results_dir:
        return None

    report_dir = Path(results_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    environment = {
        "Test.Environment": "ParaBank Demo / ProCredit (configured site)",
        "Operating.System": platform.system(),
        "OS.Release": platform.release(),
        "Python.Version": platform.python_version(),
        "Selenium.Version": _package_version("selenium"),
        "Pytest.Version": _package_version("pytest"),
        "Browser": browser_name or os.getenv("BROWSER", "chrome"),
        "Browser.Version": browser_version or "not detected",
        "Headless": os.getenv("HEADLESS", "false").lower(),
        "CI.Provider": "Jenkins" if os.getenv("BUILD_NUMBER") else "Local",
        "Jenkins.Job": os.getenv("JOB_NAME", "local"),
        "Jenkins.Build": os.getenv("BUILD_NUMBER", "local"),
    }

    result = report_dir / "environment.properties"
    result.write_text("".join(f"{k}={_clean(v)}\n" for k, v in environment.items()), encoding="utf-8")
    return result
