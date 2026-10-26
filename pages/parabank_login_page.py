from selenium.webdriver.common.by import By

from elements.button import Button
from elements.input import Input
from utils.DriverUtils import DriverUtils
from pages.base_form import BaseForm


class ParaBankLoginPage(BaseForm):
    __username = Input(By.NAME, "username", "პარაბანკის უზერი")
    __password = Input(By.NAME, "password", "პარაბანკის პაროლი")
    __login_button = Button(By.CSS_SELECTOR, "#loginPanel input[type='submit']", "ლოგინ ღილაკი")

    def __init__(self, test_data):
        super().__init__(By.ID, "loginPanel", "პარაბანკის ლოგინ პეიჯი")
        self.test_data = test_data

    def fill_username(self):
        DriverUtils.wait_for_visible((self.__username.by, self.__username.locator))
        self.__username.clear_and_fill(self.test_data.username)

    def fill_password(self):
        self.__password.clear_and_fill(self.test_data.password)

    def click_login(self):
        DriverUtils.wait_until_loader_disappears()
        self.__login_button.click()

    def verify_login_successful(self):
        DriverUtils.wait_for_presence(
            (By.CSS_SELECTOR, "#leftPanel a[href*='overview.htm']"),
            message="Login failed: Accounts Overview link did not appear"
        )
