
import allure

from pages.procreditbank_accounts_page import ProcreditAccountsPage
from pages.procreditbank_dashboard_page import ProcreditDashboardPage
from pages.procreditbank_domestic_payment_page import ProcreditDomesticPaymentPage
from pages.procreditbank_transfers_page import ProcreditTransfersPage
from steps.procreditbank_login_page_steps import LoginPageSteps
from utils.AndroidSmsOtpProvider import AndroidSmsOtpProvider
from utils.ProcreditTestData import ProcreditTestData


class ProcreditNegativeTransferSteps:
    @staticmethod
    def negative_transfer_steps(mobile=False):
        test_data = ProcreditTestData.from_environment()

        with allure.step('1. ProCredit ავტორიზაცია SMS OTP-ით'):
            dashboard = LoginPageSteps.login_page_steps()

        with allure.step('2. Dashboard-ის GEL ბალანსის წაკითხვა'):
            dashboard_balance = dashboard.get_current_balance()

        with allure.step('3. ანგარიშები — GEL ბალანსების შედარება'):
            if mobile:
                dashboard.ensure_mobile_menu_open()
            dashboard.open_accounts()
            accounts = ProcreditAccountsPage()
            accounts.is_visible()
            available_balance = accounts.verify_matches_dashboard(dashboard_balance)

        with allure.step('4. გადარიცხვები → საქართველოში'):
            transfers = ProcreditTransfersPage()
            if mobile:
                dashboard.ensure_mobile_menu_open(section='transfers')
                transfers.open_mobile_domestic_transfer()
            else:
                dashboard.open_transfers()
                transfers.is_visible()
                transfers.open_domestic_transfer()
            domestic = ProcreditDomesticPaymentPage()
            domestic.is_visible()

        with allure.step('5. მიმღების ანგარიში და ბანკის ამოცნობა'):
            domestic.enter_iban(test_data.recipient_iban)
            domestic.verify_detected_bank(test_data.expected_bank_name)

        with allure.step('6. მიმღების სახელი და ბალანსზე მეტი თანხა'):
            domestic.enter_recipient_name(test_data.recipient_name)
            requested_amount = domestic.enter_amount_over_balance(available_balance)
            domestic.verify_amount_exceeds_balance(available_balance, requested_amount)
            domestic.verify_transfer_controls_present()

        with allure.step('7. TAN კონფიგურაცია და ძველი SMS-ების დამახსოვრება'):
            provider = AndroidSmsOtpProvider.from_environment()
            domestic.verify_tan_length_configuration(provider.code_length)
            previous_ids = provider.snapshot_ids()

        with allure.step('8. SMS-ის მოთხოვნა და დადასტურება'):
            domestic.request_transfer_sms()
            domestic.confirm_transfer_sms_request()

        with allure.step('9. ახალი ოთხნიშნა TAN-ის შეყვანა'):
            tan = provider.wait_for_new_code(previous_ids, timeout=90, purpose='transfer')
            try:
                domestic.enter_transfer_tan(tan)
            finally:
                del tan

        with allure.step('10. ერთჯერადი გადარიცხვის მცდელობა და უარყოფითი შეტყობინება'):
            domestic.submit_once_and_read_insufficient_funds_warning()

        with allure.step('11. GEL ბალანსი უარყოფილი გადარიცხვის შემდეგ უცვლელია'):
            domestic.dismiss_insufficient_funds_warning()
            dashboard = ProcreditDashboardPage()
            if mobile:
                dashboard.ensure_mobile_menu_open()
            dashboard.open_accounts()
            accounts = ProcreditAccountsPage()
            accounts.is_visible()
            accounts.verify_balance_unchanged(available_balance)
