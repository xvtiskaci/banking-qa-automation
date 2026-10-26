from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from elements.button import Button
from elements.element import Element
from elements.input import Input
from managers.DriverManager import DriverManager
from utils.DriverUtils import DriverUtils
from pages.base_form import BaseForm


class TransferFundsPage(BaseForm):
    __menu_link = Button(
        By.CSS_SELECTOR, "#leftPanel a[href*='transfer.htm']", "Transfer Funds menu"
    )
    __amount = Input(By.ID, "amount", "გადარიცხვის თანხის ოდენობა")
    __from_account = Element(By.ID, "fromAccountId", "გამცემი ანგარიში")
    __to_account = Element(By.ID, "toAccountId", "მიმღები ანგარიში")
    __submit = Button(By.CSS_SELECTOR, "#transferForm input[type='submit']", "გზავნილის დათანხმების ღილაკი")

    def __init__(self, test_data):
        super().__init__(By.ID, "transferForm", "გადარიცხვების გვერდი")
        self.test_data = test_data

    def open(self):
        self.__menu_link.click()
        DriverUtils.wait_for_visible(
            (self.__amount.by, self.__amount.locator),
            message="Transfer Funds amount input is not visible"
        )

    def fill_amount(self):
        self.__amount.clear_and_fill(format(self.test_data.amount, "f"))

    @staticmethod
    def _select_account(element: Element, account_id: str):
        DriverUtils.wait_until(
            lambda d: any(option.get_attribute("value") == account_id
                          for option in Select(element.find_element()).options),
            message=f"Account {account_id} missing from {element.name} dropdown"
        )
        Select(element.find_element()).select_by_value(account_id)

    def select_from_account(self):
        self._select_account(self.__from_account, self.test_data.from_account_id)

    def select_to_account(self):
        self._select_account(self.__to_account, self.test_data.to_account_id)

    def click_transfer(self):
        self.__submit.click()

    def verify_transfer_confirmation(self):
        driver = DriverManager.get_driver()

        def finished(d):
            success = d.find_elements(By.ID, "showResult")
            errors = d.find_elements(By.ID, "showError")
            return any(e.is_displayed() for e in success + errors)

        DriverUtils.wait_until(
            finished, message="No transfer result or error was displayed"
        )
        assert not any(e.is_displayed() for e in driver.find_elements(By.ID, "showError")), (
            "ParaBank displayed a transfer error (#showError)"
        )

        actual_amount = Element(By.ID, "amountResult", "Result amount").get_text()
        actual_from = Element(By.ID, "fromAccountIdResult", "Result source").get_text()
        actual_to = Element(By.ID, "toAccountIdResult", "Result target").get_text()

        expected_amount = f"${self.test_data.amount:,.2f}"
        assert actual_amount.strip() == expected_amount, (
            f"Wrong transfer amount in confirmation: {actual_amount!r} != {expected_amount!r}"
        )
        assert actual_from.strip() == self.test_data.from_account_id, (
            f"Wrong sender account in confirmation: {actual_from}"
        )
        assert actual_to.strip() == self.test_data.to_account_id, (
            f"Wrong recipient account in confirmation: {actual_to}"
        )
