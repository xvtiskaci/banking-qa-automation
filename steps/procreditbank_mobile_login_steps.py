import allure

from pages.procreditbank_dashboard_page import ProcreditDashboardPage
from pages.procreditbank_login_page import ProcreditLoginPage
from utils.AndroidSmsOtpProvider import AndroidSmsOtpProvider


class ProcreditMobileLoginSteps:
    @staticmethod
    def mobile_login_steps():
        with allure.step('Responsive mobile: ProCredit ავტორიზაცია'):
            page = ProcreditLoginPage()
            page.is_visible()
            provider = AndroidSmsOtpProvider.from_environment()
            sms_before = provider.snapshot_ids()
            page.fill_user()
            page.fill_user_password()
            page.click_submit_button()

        with allure.step('ახალი SMS OTP-ით შესვლა'):
            code = provider.wait_for_new_code(sms_before, timeout=90, purpose="login")
            page.fill_otp_code(code)
            page.click_sms_submit()
            del code

        with allure.step('Dashboard-ის ჩატვირთვის შემოწმება'):
            dashboard = ProcreditDashboardPage()
            dashboard.is_visible()
        return dashboard
