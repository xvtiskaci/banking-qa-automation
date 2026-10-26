import os

from selenium.webdriver.common.by import By

from elements.button import Button
from elements.input import Input
from pages.base_form import BaseForm
from utils.DriverUtils import DriverUtils


class ProcreditLoginPage(BaseForm):
    __user_input = Input(By.ID, 'auth_login_username', 'ProCredit login username')
    __user_password = Input(By.ID, 'auth_login_password', 'ProCredit login password')
    __click_submit = Button(By.XPATH, "//button[contains(normalize-space(.),'შესვლა')]",'Login submit')
    __otp_input = Input(By.XPATH,"//input[@placeholder='ავთენტიფიკაციის კოდი' and @type='password']",'Login OTP input')
    __sms_submit = Button(By.ID, 'tanInput', 'Confirm login OTP')
    __cookie_consent = Button(
        By.XPATH,
        "//button[contains(concat(' ', normalize-space(@class), ' '), ' button_red ') "
        "and contains(concat(' ', normalize-space(@class), ' '), ' button_s ') "
        "and normalize-space(.)='ვეთანხმები']",
        'Accept cookie notice',)

    def __init__(self):
        super().__init__(By.ID, 'auth_login_username', 'ProCredit sign-in page')

    def fill_user(self):
        username = os.getenv('PRO_CREDIT_USERNAME', '').strip()
        if not username:
            raise ValueError('Set PRO_CREDIT_USERNAME in the environment')
        DriverUtils.wait_for_visible((self.__user_input.by, self.__user_input.locator))
        self.__user_input.clear_and_fill(username)

    def fill_user_password(self):
        password = os.getenv('PRO_CREDIT_PASSWORD', '')
        if not password:
            raise ValueError('Set PRO_CREDIT_PASSWORD in the environment')
        self.__user_password.clear_and_fill(password)

    def accept_cookie_consent_if_visible(self):

        visible_buttons = [
            element for element in self.__cookie_consent.find_elements()
            if element.is_displayed()
        ]
        if not visible_buttons:
            return False

        locator = (self.__cookie_consent.by, self.__cookie_consent.locator)
        DriverUtils.wait_for_unobstructed(locator).click()
        DriverUtils.wait_until(
            lambda _driver: not any(
                element.is_displayed()
                for element in self.__cookie_consent.find_elements()
            ),
            message='Cookie consent popup did not close after accepting it',
        )
        return True

    def click_submit_button(self):
        DriverUtils.wait_until_loader_disappears()
        submit = DriverUtils.wait_for_unobstructed(
            (self.__click_submit.by, self.__click_submit.locator)
        )
        submit.click()

    def fill_otp_code(self, code):
        DriverUtils.wait_for_visible((self.__otp_input.by, self.__otp_input.locator))
        self.__otp_input.clear_and_fill(str(code))

    def click_sms_submit(self):
        otp_confirm = DriverUtils.wait_for_unobstructed(
            (self.__sms_submit.by, self.__sms_submit.locator)
        )
        otp_confirm.click()
