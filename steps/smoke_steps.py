import allure

from pages.parabank_login_page import ParaBankLoginPage
from pages.parabank_accounts_overview_page import AccountsOverviewPage
from utils.SmokeTestData import SmokeTestData


class SmokeSteps:
    @staticmethod
    def login_and_verify_accounts():
        test_data = SmokeTestData.from_environment()

        with allure.step("1. ParaBank მომხმარებლის ავტორიზაცია"):
            login = ParaBankLoginPage(test_data)
            login.is_visible()
            login.fill_username()
            login.fill_password()
            login.click_login()
            login.verify_login_successful()

        with allure.step("2. Accounts Overview გვერდის ჩატვირთვის დადასტურება"):
            overview = AccountsOverviewPage(test_data)
            overview.open()
            overview.verify_any_account_visible()
