import os

import allure
import pytest

from data.models.data_for_procreditbank import DataForProcreditBank

DataForProcreditBank.configure()

from managers.DriverManager import DriverManager
from utils.ParserUtils import ParserUtils
from utils.AllureEnvironment import write_allure_environment


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, "rep_" + report.when, report)


@pytest.fixture(autouse=True, scope="function")
def set_up(request):
    marker = request.node.get_closest_marker("site")
    if marker is None or len(marker.args) != 1:
        raise pytest.UsageError(
            f"{request.node.nodeid}: add @pytest.mark.site('procreditbank') "
            "or @pytest.mark.site('parabank')"
        )

    site_name = marker.args[0]
    urls = ParserUtils.parse_json("config.json")["urls"]
    if site_name not in urls:
        raise pytest.UsageError(
            f"Unknown site {site_name!r}; available sites: {', '.join(urls)}"
        )
    url = urls[site_name]
    if site_name == 'procreditbank':
        url = os.getenv('PRO_CREDIT_BASE_URL', url)
    elif site_name == 'parabank':
        url = os.getenv('PARABANK_BASE_URL', url)

    browser = os.getenv("BROWSER", "chrome")
    driver = DriverManager.get_driver(browser)

    capabilities = getattr(driver, "capabilities", {}) or {}
    request.config._parabank_browser_name = str(capabilities.get("browserName", browser))
    request.config._parabank_browser_version = str(capabilities.get("browserVersion", "not detected"))
    try:
        driver.set_window_size(1920, 1080)
        driver.get(url)
        yield
    finally:
        report = getattr(request.node, "rep_call", None)
        if site_name != 'procreditbank' and report is not None and report.failed:
            try:
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name="Screenshot - ტესტის ჩავარდნა",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception as exc:
                print(f"Could not attach Allure screenshot: {type(exc).__name__}")
        DriverManager.close_driver()


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    results_dir = session.config.getoption("allure_report_dir", default=None)
    if not results_dir:
        return
    write_allure_environment(
        results_dir,
        browser_name=getattr(session.config, "_parabank_browser_name", None),
        browser_version=getattr(session.config, "_parabank_browser_version", None),
    )

def pytest_collection_modifyitems(items):

    for item in items:
        site = item.get_closest_marker("site")

        if not site or not site.args:
            continue

        if site.args[0] != "procreditbank":
            continue

        if os.getenv("PRO_CREDIT_RUN") != "1":
            item.add_marker(pytest.mark.skip(
                reason="ProCredit tests are disabled"
            ))
            continue

        if item.get_closest_marker("livebank") is None:
            continue

        if os.getenv("PRO_CREDIT_NEGATIVE_SUBMIT") != "YES":
            item.add_marker(pytest.mark.skip(
                reason="Live bank submission is disabled"
            ))
            continue

        if os.getenv("HEADLESS", "false").strip().lower() in (
            "1", "true", "yes"
        ):
            item.add_marker(pytest.mark.skip(
                reason="Live bank tests require visible Chrome"
            ))
            continue

        if item.get_closest_marker("procredit_mobile"):

            if os.getenv(
                "PRO_CREDIT_MOBILE_NEGATIVE_SUBMIT"
            ) != "YES":

                item.add_marker(pytest.mark.skip(
                    reason="Mobile live transfer is disabled"
                ))

@pytest.fixture(autouse=True)
def mobile_viewport(request, set_up):

    if request.node.get_closest_marker("procredit_mobile") is None:
        yield
        return

    driver = DriverManager.get_driver()

    browser_name = (
        driver.capabilities.get("browserName") or ""
    ).lower()

    if browser_name != "chrome":
        pytest.fail("Mobile responsive tests require Chrome")

    driver.execute_cdp_cmd(
        "Emulation.setDeviceMetricsOverride",
        {
            "width": 414,
            "height": 896,
            "deviceScaleFactor": 3,
            "mobile": True,
            "screenWidth": 414,
            "screenHeight": 896,
        }
    )

    driver.execute_cdp_cmd(
        "Emulation.setTouchEmulationEnabled",
        {
            "enabled": True,
            "maxTouchPoints": 1,
        }
    )

    driver.refresh()

    viewport_width = driver.execute_script(
        "return window.innerWidth"
    )

    assert viewport_width == 414, (
        f"Expected mobile viewport 414, got {viewport_width}"
    )

    yield