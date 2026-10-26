from selenium.webdriver.common.by import By

from elements.element import Element
from utils.DriverUtils import DriverUtils
from pages.base_form import BaseForm
from utils.ProcreditMoney import parse_gel_amount


class ProcreditAccountsPage(BaseForm):
    __gel_available_balance = Element(
        By.XPATH,
        "//a[starts-with(@href,'/dashboard/accounts/') and contains(.,'GEL')]"
        "//span[normalize-space()='ხელმისაწვდომი']/following-sibling::strong[1]",
        'GEL available balance',
    )

    def __init__(self):
        super().__init__(By.XPATH, "//a[starts-with(@href,'/dashboard/accounts/') and contains(.,'GEL')]",
                         'GEL current account card')

    def get_gel_available_balance(self):
        locator = (self.__gel_available_balance.by, self.__gel_available_balance.locator)
        element = DriverUtils.wait_for_visible(locator)
        return parse_gel_amount(element.text)

    def verify_matches_dashboard(self, dashboard_balance):
        current = self.get_gel_available_balance()
        assert current == dashboard_balance, (
            f'Balances do not match: Dashboard={dashboard_balance}, Accounts={current}'
        )
        return current

    def verify_balance_unchanged(self, before_balance):
        after = self.get_gel_available_balance()
        assert after == before_balance, (
            f'GEL balance changed: before={before_balance}, after={after}. '
            'Check account activity before attempting another transfer.'
        )
        return after
