from selenium.webdriver.common.by import By

from elements.button import Button
from managers.DriverManager import DriverManager
from elements.element import Element
from utils.DriverUtils import DriverUtils
from pages.base_form import BaseForm
from utils.ProcreditMoney import parse_gel_amount


class ProcreditDashboardPage(BaseForm):
    __mobile_menu_button = Button(
        By.XPATH,
        "//header[@id='site-header']"
        "//div[contains(concat(' ', normalize-space(@class), ' '), ' burger ')]",
        'ProCredit mobile hamburger menu',
    )
    __current_balance = Element(
        By.XPATH,
        "//li[.//div[normalize-space()='მიმდინარე']]//span[contains(@class,'text-color')]",
        'Dashboard current balance',
    )
    __accounts_menu = Button(By.XPATH, "//a[@href='/dashboard/accounts']", 'Accounts navigation')
    __mobile_transfers_menu = Button(
        By.XPATH, "//a[@href='/dashboard/transfers']", 'Mobile Transfers navigation'
    )
    __transfers_menu = Button(
        By.XPATH,
        "//a[contains(normalize-space(.),'გადარიცხვები') and "
        "(contains(@href,'/dashboard/transfers') or not(@href))]",
        'Transfers navigation',
    )

    def __init__(self):
        super().__init__(By.XPATH, "//li[.//div[normalize-space()='მიმდინარე']]", 'ProCredit dashboard')

    def get_current_balance(self):
        locator = (self.__current_balance.by, self.__current_balance.locator)
        element = DriverUtils.wait_for_visible(locator)
        return parse_gel_amount(element.text)

    def open_accounts(self):
        locator = (self.__accounts_menu.by, self.__accounts_menu.locator)
        DriverUtils.wait_for_clickable(locator).click()

    def open_transfers(self):
        locator = (self.__transfers_menu.by, self.__transfers_menu.locator)
        DriverUtils.wait_for_clickable(locator).click()

    def open_mobile_menu(self):
        menu_locator = (self.__mobile_menu_button.by, self.__mobile_menu_button.locator)
        DriverUtils.wait_for_clickable(menu_locator).click()

    def ensure_mobile_menu_open(self, section='accounts'):
        if section not in ('accounts', 'transfers'):
            raise ValueError('Unknown mobile navigation section: ' + section)
        item = self.__accounts_menu if section == 'accounts' else self.__mobile_transfers_menu
        locator = (item.by, item.locator)
        driver = DriverManager.get_driver()

        def visible_sidebar_link(browser):
            for item in browser.find_elements(*locator):
                if item.is_displayed() and browser.execute_script(
                    "const r = arguments[0].getBoundingClientRect(); "
                    "return r.width > 0 && r.height > 0 && "
                    "r.left < innerWidth && r.right > 0 && "
                    "r.top < innerHeight && r.bottom > 0;",
                    item,
                ):
                    return item
            return False

        if not visible_sidebar_link(driver):
            self.open_mobile_menu()
        DriverUtils.wait_until(
            visible_sidebar_link,
            message=f'Responsive sidebar did not reveal {section} navigation',
        )
