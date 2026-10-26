from collections import Counter
from decimal import Decimal
import re

from selenium.webdriver.common.by import By

from elements.button import Button
from managers.DriverManager import DriverManager
from utils.DriverUtils import DriverUtils
from pages.base_form import BaseForm
from utils.LoggerUtils import LoggerUtils


class AccountActivityPage(BaseForm):
    __overview_link = Button(By.CSS_SELECTOR, "#leftPanel a[href*='overview.htm']", "Accounts Overview")

    def __init__(self, test_data):
        super().__init__(By.ID, "transactionTable", "Account activity page")
        self.test_data = test_data
        self._sender_history_before = None
        self._receiver_history_before = None

    def open_account(self, account_id: str):
        driver = DriverManager.get_driver()
        self.__overview_link.click()

        def account_link(d):
            for link in d.find_elements(By.CSS_SELECTOR, "#accountTable a"):
                if link.text.strip() == account_id:
                    return link
            return False

        DriverUtils.wait_until(
            account_link, message=f"Account {account_id} not found"
        ).click()

        def loaded(d):
            panel = d.find_element(By.ID, "rightPanel")
            table = d.find_element(By.ID, "transactionTable")
            return (table.is_displayed() and "Account Details" in panel.text
                    and account_id in panel.text)

        DriverUtils.wait_until(
            loaded, message=f"Account activity did not load for {account_id}"
        )

    def open_sender_account(self):
        self.open_account(self.test_data.from_account_id)

    def open_receiver_account(self):
        self.open_account(self.test_data.to_account_id)

    @staticmethod
    def _parse_money(value: str):
        normalized = re.sub(r"[^\d.\-]", "", value.strip())
        return Decimal(normalized) if normalized else None

    def _snapshot(self) -> Counter:
        def visible_rows(driver):
            table = driver.find_element(By.ID, "transactionTable")
            if not table.is_displayed():
                return False
            rows = Counter()
            for row in table.find_elements(By.CSS_SELECTOR, "tbody tr"):
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) != 4:
                    continue
                key = (
                    cells[0].text.strip(),
                    cells[1].text.strip(),
                    self._parse_money(cells[2].text),
                    self._parse_money(cells[3].text),
                )
                rows[key] += 1
            return (True, rows)

        return DriverUtils.wait_until(visible_rows)[1]

    def save_sender_history(self):
        self._sender_history_before = self._snapshot()
        LoggerUtils.info("Saved sender transaction history before transfer")

    def save_receiver_history(self):
        self._receiver_history_before = self._snapshot()
        LoggerUtils.info("Saved receiver transaction history before transfer")

    def _verify_new_entry(self, original: Counter, direction: str, account_id: str):
        assert original is not None, f"No initial history snapshot for {account_id}"
        new_entries = self._snapshot() - original
        amount = self.test_data.amount
        valid = any(
            "transfer" in description.lower() and
            (debit == amount if direction == "debit" else credit == amount)
            for (_date, description, debit, credit), count in new_entries.items()
            if count > 0
        )
        assert valid, f"No NEW transfer {direction} of {amount} found for {account_id}"

    def verify_new_sender_debit(self):
        self._verify_new_entry(
            self._sender_history_before, "debit", self.test_data.from_account_id
        )

    def verify_new_receiver_credit(self):
        self._verify_new_entry(
            self._receiver_history_before, "credit", self.test_data.to_account_id
        )
