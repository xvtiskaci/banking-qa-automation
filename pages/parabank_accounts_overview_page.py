import re
from decimal import Decimal

from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.by import By

from elements.button import Button
from utils.DriverUtils import DriverUtils
from pages.base_form import BaseForm
from utils.LoggerUtils import LoggerUtils


class AccountsOverviewPage(BaseForm):
    __overview_link = Button(
        By.CSS_SELECTOR, "#leftPanel a[href*='overview.htm']", "Accounts Overview"
    )

    def __init__(self, test_data):
        super().__init__(By.ID, "accountTable", "Accounts Overview page")
        self.test_data = test_data
        self._balances_before = None

    def open(self):
        self.__overview_link.click()
        DriverUtils.wait_for_visible(
            (By.ID, "accountTable"), message="Accounts Overview table did not become visible"
        )

    @staticmethod
    def _parse_balance(value: str) -> Decimal:
        normalized = re.sub(r"[^\d.\-]", "", value.strip())
        if not normalized:
            raise ValueError(f"Could not parse displayed account balance: {value!r}")
        return Decimal(normalized)

    def _read_selected_balances(self) -> dict[str, Decimal]:
        account_ids = (self.test_data.from_account_id, self.test_data.to_account_id)

        def get_balances(driver):
            try:
                balances = {}
                for row in driver.find_elements(By.CSS_SELECTOR, "#accountTable tbody tr"):
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) < 2:
                        continue
                    links = cells[0].find_elements(By.TAG_NAME, "a")
                    if links:
                        balances[links[0].text.strip()] = self._parse_balance(cells[1].text)
                return {account: balances[account] for account in account_ids} if all(
                    account in balances for account in account_ids
                ) else False
            except (StaleElementReferenceException, NoSuchElementException, ValueError):
                return False

        return DriverUtils.wait_until(
            get_balances,
            message=f"Accounts {account_ids} were not loaded in Accounts Overview"
        )

    def save_initial_balances(self):
        self._balances_before = self._read_selected_balances()
        LoggerUtils.info(f"Balances before transfer: {self._balances_before}")

    def verify_sufficient_balance(self):
        assert self._balances_before is not None, "Save initial balances before checking them"
        sender = self.test_data.from_account_id
        assert self._balances_before[sender] >= self.test_data.amount, (
            f"Insufficient test balance on {sender}: "
            f"{self._balances_before[sender]} < {self.test_data.amount}"
        )

    def verify_balances_after_transfer(self):
        assert self._balances_before is not None, "Initial balances were not saved"
        after = self._read_selected_balances()
        before = self._balances_before
        sender = self.test_data.from_account_id
        receiver = self.test_data.to_account_id
        amount = self.test_data.amount
        LoggerUtils.info(f"Balances after transfer: {after}")

        assert after[sender] == before[sender] - amount, (
            f"Sender balance incorrect: {before[sender]} -> {after[sender]}"
        )
        assert after[receiver] == before[receiver] + amount, (
            f"Receiver balance incorrect: {before[receiver]} -> {after[receiver]}"
        )
        assert after[sender] + after[receiver] == before[sender] + before[receiver], (
            "Total balance of participating accounts changed"
        )

    def verify_any_account_visible(self):
        def account_loaded(driver):
            links = driver.find_elements(By.CSS_SELECTOR, "#accountTable td a")
            return any(link.is_displayed() and link.text.strip().isdigit() for link in links)

        DriverUtils.wait_until(
            account_loaded,
            message="Smoke failed: no account ID is visible in Accounts Overview"
        )
