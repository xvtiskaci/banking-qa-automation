import allure

from pages.parabank_login_page import ParaBankLoginPage
from pages.parabank_accounts_overview_page import AccountsOverviewPage
from pages.parabank_transfer_funds_page import TransferFundsPage
from pages.parabank_account_activity_page import AccountActivityPage
from utils.TransferTestData import TransferTestData


class TransferFundsSteps:
    @staticmethod
    def successful_transfer():
        test_data = TransferTestData.from_environment()

        with allure.step("1. მომხმარებლის ავტორიზაცია"):
            login_page = ParaBankLoginPage(test_data)
            login_page.is_visible()
            login_page.fill_username()
            login_page.fill_password()
            login_page.click_login()
            login_page.verify_login_successful()

        with allure.step("2. საწყისი ბალანსები და საკმარისი თანხა"):
            accounts_page = AccountsOverviewPage(test_data)
            accounts_page.open()
            accounts_page.save_initial_balances()
            accounts_page.verify_sufficient_balance()

        with allure.step("3. Debit/Credit ისტორიის შენახვა გადარიცხვამდე"):
            activity_page = AccountActivityPage(test_data)
            activity_page.open_sender_account()
            activity_page.save_sender_history()
            activity_page.open_receiver_account()
            activity_page.save_receiver_history()

        with allure.step("4. შიდა გადარიცხვის შესრულება და დადასტურება"):
            transfer_page = TransferFundsPage(test_data)
            transfer_page.open()
            transfer_page.fill_amount()
            transfer_page.select_from_account()
            transfer_page.select_to_account()
            transfer_page.click_transfer()
            transfer_page.verify_transfer_confirmation()

        with allure.step("5. ბალანსების ფინანსური შედარება"):
            accounts_page.open()
            accounts_page.verify_balances_after_transfer()

        with allure.step("6. ახალი Debit და Credit ჩანაწერების შემოწმება"):
            activity_page.open_sender_account()
            activity_page.verify_new_sender_debit()
            activity_page.open_receiver_account()
            activity_page.verify_new_receiver_credit()
