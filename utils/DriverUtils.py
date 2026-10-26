

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from managers.DriverManager import DriverManager
from utils.ElementFinder import ElementFinder
from selenium.webdriver.support import expected_conditions as EC


class DriverUtils:
    VISIBLE_TIMEOUT = 25
    CLICKABLE_TIMEOUT = 25
    PRESENCE_TIMEOUT = 25
    DYNAMIC_TIMEOUT = 35
    ATTRIBUTE_TIMEOUT = 60
    ALERT_TIMEOUT = 10
    POLL_INTERVAL = 0.25
    IGNORED_EXCEPTIONS = (NoSuchElementException, StaleElementReferenceException)

    @staticmethod
    def _wait(timeout, poll_frequency=None, ignored_exceptions=None):
        return WebDriverWait(
            DriverManager.get_driver(),
            timeout=timeout,
            poll_frequency=(DriverUtils.POLL_INTERVAL if poll_frequency is None
                            else poll_frequency),
            ignored_exceptions=(DriverUtils.IGNORED_EXCEPTIONS if ignored_exceptions is None
                                else ignored_exceptions),
        )

    @staticmethod
    def find_element(xpath):
        return DriverManager.get_driver().find_element(By.XPATH, xpath)

    @staticmethod
    def wait_for_element_enable(element):
        return DriverUtils.wait_for_clickable(element)

    @staticmethod
    def wait_for_changes(locator, attribute, text):
        return DriverUtils._wait(DriverUtils.ATTRIBUTE_TIMEOUT).until(
            expected_conditions.text_to_be_present_in_element_attribute(locator, attribute, text)
        )

    @staticmethod
    def wait_for_visible(locator, message=None):
        def element_is_visible(_driver):
            element = ElementFinder.find_element(locator[0], locator[1])
            return element if element.is_displayed() else False

        return DriverUtils._wait(DriverUtils.VISIBLE_TIMEOUT).until(
            element_is_visible, message=message or 'Element did not become visible'
        )

    @staticmethod
    def wait_for_presence(locator, message=None):
        return DriverUtils._wait(DriverUtils.PRESENCE_TIMEOUT).until(
            lambda _driver: ElementFinder.find_element(locator[0], locator[1]),
            message=message or 'Element was not found',
        )

    @staticmethod
    def wait_for_alert_visible():
        return DriverUtils._wait(DriverUtils.ALERT_TIMEOUT).until(
            expected_conditions.alert_is_present()
        )

    @staticmethod
    def wait_for_clickable(element, message=None):
        if isinstance(element, tuple):
            def predicate(_driver):
                candidate = ElementFinder.find_element(element[0], element[1])
                return candidate if candidate.is_displayed() and candidate.is_enabled() else False
        else:
            predicate = expected_conditions.element_to_be_clickable(element)
        return DriverUtils._wait(DriverUtils.CLICKABLE_TIMEOUT).until(
            predicate, message=message or 'Element was not clickable'
        )

    @staticmethod
    def wait_until(condition, message=None, ignored_exceptions=None):
        return DriverUtils._wait(
            DriverUtils.DYNAMIC_TIMEOUT, ignored_exceptions=ignored_exceptions
        ).until(condition, message=message or '')

    @staticmethod
    def switch_to_iframe(web_element):
        return DriverManager.get_driver().switch_to.frame(web_element.find_element())

    @staticmethod
    def go_back():
        DriverManager.get_driver().back()

    @staticmethod
    def scroll_up(pixels=400):
        DriverManager.get_driver().execute_script('window.scrollBy(0, -arguments[0]);', pixels)

    @staticmethod
    def scroll_down(pixels=200):
        DriverManager.get_driver().execute_script('window.scrollBy(0, arguments[0]);', pixels)

    @staticmethod
    def wait_until_loader_disappears(timeout=30):
        WebDriverWait(
            DriverManager.get_driver(), timeout
        ).until(
            EC.invisibility_of_element_located(
                (By.CSS_SELECTOR, "div.loader-wrap")
            )
        )

    @staticmethod
    def wait_for_unobstructed(locator, timeout=None):

        from selenium.common.exceptions import TimeoutException

        last_blocker = {'description': 'not visible or not enabled'}

        def target_is_unobstructed(driver):
            target = ElementFinder.find_element(locator[0], locator[1])
            if not (target.is_displayed() and target.is_enabled()):
                return False

            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});",
                target,
            )
            hit_test = driver.execute_script(
                r"""
                const target = arguments[0];
                const rect = target.getBoundingClientRect();
                const left = Math.max(0, rect.left);
                const right = Math.min(window.innerWidth, rect.right);
                const top = Math.max(0, rect.top);
                const bottom = Math.min(window.innerHeight, rect.bottom);
                if (right <= left || bottom <= top) {
                    return {ok: false, blocker: 'outside viewport'};
                }
                const x = Math.floor((left + right) / 2);
                const y = Math.floor((top + bottom) / 2);
                const hit = document.elementFromPoint(x, y);
                if (hit === target || target.contains(hit)) {
                    return {ok: true};
                }
                return {
                    ok: false,
                    blocker: hit ? (
                        hit.tagName.toLowerCase() +
                        (hit.id ? '#' + hit.id : '') +
                        (typeof hit.className === 'string' && hit.className
                            ? '.' + hit.className.trim().split(/\s+/).slice(0, 2).join('.')
                            : '')
                    ) : 'no element at target centre'
                };
                """,
                target,
            )
            if hit_test['ok']:
                return target
            last_blocker['description'] = hit_test['blocker']
            return False

        try:
            return DriverUtils._wait(timeout or DriverUtils.DYNAMIC_TIMEOUT).until(
                target_is_unobstructed,
                message='Target remained covered at its visible centre',
            )
        except TimeoutException as exc:
            raise TimeoutException(
                'Target could not be clicked safely; covering element: '
                + last_blocker['description']
            ) from exc
