from selenium.webdriver.common.by import By

from elements.button import Button
from managers.DriverManager import DriverManager
from pages.base_form import BaseForm
from utils.DriverUtils import DriverUtils


class ProcreditTransfersPage(BaseForm):
    __domestic_transfer = Button(
        By.XPATH,
        "//a[@href='/dashboard/transfers/domestic-payment']",
        'Transfers in Georgia',
    )
    __mobile_transfers_toggle = Button(
        By.XPATH,
        "//a[@href='/dashboard/transfers']",
        'Mobile Transfers accordion',
    )
    __mobile_domestic_transfer = Button(
        By.XPATH,
        "//a[@href='/dashboard/transfers/domestic-payment' "
        "and normalize-space(.)='საქართველოში']",
        'Mobile domestic payment (Georgia)',
    )

    def __init__(self):
        super().__init__(
            self.__domestic_transfer.by,
            self.__domestic_transfer.locator,
            'ProCredit transfers menu',
        )

    def open_domestic_transfer(self):
        locator = (self.__domestic_transfer.by, self.__domestic_transfer.locator)
        DriverUtils.wait_for_clickable(locator).click()

    @staticmethod
    def _visible_enabled(driver, locator):
        for item in driver.find_elements(*locator):
            if item.is_displayed() and item.is_enabled():
                return item
        return False

    def open_mobile_domestic_transfer(self):
        driver = DriverManager.get_driver()
        toggle_locator = (
            self.__mobile_transfers_toggle.by,
            self.__mobile_transfers_toggle.locator,
        )
        georgia_locator = (
            self.__mobile_domestic_transfer.by,
            self.__mobile_domestic_transfer.locator,
        )

        if not self._visible_enabled(driver, georgia_locator):
            toggle = DriverUtils.wait_until(
                lambda browser: self._visible_enabled(browser, toggle_locator),
                message='Mobile Transfers link is not visible in the opened sidebar',
            )
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", toggle,
            )
            toggle.click()

        georgia = DriverUtils.wait_until(
            lambda browser: self._visible_enabled(browser, georgia_locator),
            message='Mobile Transfers submenu did not show the საქართველოში link',
        )
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", georgia,
        )
        georgia.click()
