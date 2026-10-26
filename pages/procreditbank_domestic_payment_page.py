
from decimal import Decimal
import re

from selenium.webdriver.common.by import By

from elements.button import Button
from elements.element import Element
from elements.input import Input
from managers.DriverManager import DriverManager
from pages.base_form import BaseForm
from utils.ProcreditMoney import parse_gel_amount
from utils.DriverUtils import DriverUtils


class ProcreditDomesticPaymentPage(BaseForm):
    __iban = Input(
        By.XPATH,
        "//div[normalize-space()='მიმღების ანგარიში']"
        "/following::input[contains(@class,'local_input_styles')][1]",
        'Recipient IBAN',
    )
    __bank_name = Element(
        By.XPATH,
        "//div[normalize-space()='ბანკის დასახელება']/following-sibling::label[1]//input",
        'Automatically detected bank name',
    )
    __recipient_name = Input(
        By.XPATH,
        "//div[normalize-space()='მიმღების დასახელება']/following-sibling::label[1]//input",
        'Recipient full name',
    )
    __amount = Input(
        By.XPATH, "//div[contains(@class,'i_amount')]//input[@placeholder='0']", 'Transfer amount'
    )
    __tan_field = Element(
        By.XPATH, "//div[contains(@class,'otp-input')]//input[@placeholder='TAN']", 'TAN field'
    )
    __sms_request_control = Element(
        By.XPATH,
        "//div[contains(concat(' ',normalize-space(@class),' '),' withTan ')]"
        "//div[contains(concat(' ',normalize-space(@class),' '),' otp_wrapper ')]"
        "/following-sibling::*[1]",
        'Transfer SMS request control',
    )
    __sms_confirmation_yes = Button(
        By.XPATH,
        "//div[contains(@class,'tan-confirmation-popup')]"
        "//button[normalize-space()='დიახ']",
        'Confirm transfer SMS request',
    )
    __transfer_button = Button(
        By.XPATH, "//button[contains(@class,'button_red') and normalize-space()='გადარიცხვა']",
        'Transfer submit control',
    )
    __insufficient_funds_notification = Element(
        By.XPATH,
        "//div[contains(concat(' ',normalize-space(@class),' '),' modal ')]"
        "//span[contains(concat(' ',normalize-space(@class),' '),' text ') "
        "and contains(normalize-space(.),'თქვენ არ გაქვთ საკმარისი თანხა ანგარიშზე')]",
        'Insufficient funds notification',
    )

    def __init__(self):
        super().__init__(self.__iban.by, self.__iban.locator, 'Domestic transfer form')

    @staticmethod
    def _normalize_bank_name(value):
        return re.sub(r'[\s"“”„«»]+', '', value).casefold()

    def enter_iban(self, iban):
        locator = (self.__iban.by, self.__iban.locator)
        DriverUtils.wait_for_clickable(locator)
        self.__iban.clear_and_fill(iban)

    def verify_detected_bank(self, expected_bank):
        locator = (self.__bank_name.by, self.__bank_name.locator)
        expected = self._normalize_bank_name(expected_bank)

        def bank_is_detected(driver):
            for element in driver.find_elements(*locator):
                if element.is_displayed():
                    value = element.get_attribute('value') or ''
                    if self._normalize_bank_name(value) == expected:
                        return value
            return False

        return DriverUtils.wait_until(
            bank_is_detected,
            message='Auto-detected bank did not match the configured expected bank',
        )

    def enter_recipient_name(self, name):
        locator = (self.__recipient_name.by, self.__recipient_name.locator)
        DriverUtils.wait_for_clickable(locator)
        self.__recipient_name.clear_and_fill(name)
        actual = self.__recipient_name.find_element().get_attribute('value') or ''
        assert actual.strip() == name, 'Recipient name was not retained in the form'

    def enter_amount_over_balance(self, balance: Decimal) -> Decimal:
        balance = Decimal(str(balance))
        amount = balance + Decimal('1.00')
        locator = (self.__amount.by, self.__amount.locator)
        DriverUtils.wait_for_clickable(locator)
        self.__amount.clear_and_fill(format(amount, '.2f'))
        actual = parse_gel_amount(self.__amount.find_element().get_attribute('value') or '')
        assert actual == amount, 'The entered amount differs from the intended test amount'
        assert amount > balance, 'The invalid transfer amount must exceed the available balance'
        return amount

    def verify_transfer_controls_present(self):
        driver = DriverManager.get_driver()
        DriverUtils.wait_for_visible((self.__transfer_button.by, self.__transfer_button.locator))
        DriverUtils.wait_for_presence((self.__tan_field.by, self.__tan_field.locator))

    def request_transfer_sms(self):
        driver = DriverManager.get_driver()
        locator = (self.__sms_request_control.by, self.__sms_request_control.locator)

        def active_sms_control(driver):
            for candidate in driver.find_elements(*locator):
                classes = (candidate.get_attribute('class') or '').lower().split()
                if ('disabled-button' not in classes and 'disabled' not in classes
                        and candidate.is_displayed() and candidate.is_enabled()
                        and candidate.get_attribute('aria-disabled') != 'true'):
                    return candidate
            return False

        control = DriverUtils.wait_until(
            active_sms_control,
            message='SMS request control was not enabled; check the active SMS control outerHTML',
        )
        control.click()
        popup_locator = (self.__sms_confirmation_yes.by, self.__sms_confirmation_yes.locator)
        DriverUtils.wait_for_visible(
            popup_locator, message='Transfer SMS confirmation popup did not appear'
        )

    def confirm_transfer_sms_request(self):
        locator = (self.__sms_confirmation_yes.by, self.__sms_confirmation_yes.locator)
        DriverUtils.wait_for_clickable(locator).click()

    def enter_transfer_tan(self, tan):
        tan = str(tan)
        if not (tan.isascii() and tan.isdecimal() and len(tan) == 4):
            raise ValueError('Transfer TAN must have exactly four ASCII digits')
        locator = (self.__tan_field.by, self.__tan_field.locator)
        field = DriverUtils.wait_for_clickable(
            locator, message='Transfer TAN field is not enabled after SMS confirmation'
        )
        field.clear()
        field.send_keys(tan)

    def submit_once_and_read_insufficient_funds_warning(self):
        locator = (self.__transfer_button.by, self.__transfer_button.locator)
        button = DriverUtils.wait_for_clickable(locator)
        button.click()
        warning = self.get_insufficient_funds_warning()
        self.verify_insufficient_funds_warning(warning)
        return warning

    def dismiss_insufficient_funds_warning(self):
        driver = DriverManager.get_driver()
        close_locator = (
            By.XPATH,
            "//div[contains(concat(' ',normalize-space(@class),' '),' modal ')]"
            "[.//span[contains(@class,'text') and "
            "contains(normalize-space(.),'თქვენ არ გაქვთ საკმარისი თანხა ანგარიშზე')]]"
            "//div[contains(concat(' ',normalize-space(@class),' '),' close ')]",
        )
        for element in driver.find_elements(*close_locator):
            if element.is_displayed():
                element.click()
                break

    def get_insufficient_funds_warning(self):
        locator = (self.__insufficient_funds_notification.by,
                   self.__insufficient_funds_notification.locator)
        element = DriverUtils.wait_for_visible(
            locator, message='Insufficient funds notification did not appear',
        )
        return ' '.join(element.text.split())

    @staticmethod
    def verify_insufficient_funds_warning(warning):
        expected = 'თქვენ არ გაქვთ საკმარისი თანხა ანგარიშზე'
        assert expected in warning, (
            'Bank did not return the expected insufficient-funds rejection. '
            'Inspect bank activity before any repeat attempt.'
        )

    @staticmethod
    def verify_amount_exceeds_balance(balance, amount):
        assert Decimal(str(amount)) > Decimal(str(balance)), (
            'Refuse final submission: requested amount does not exceed available GEL balance'
        )

    @staticmethod
    def verify_tan_length_configuration(code_length):
        if code_length != 4:
            raise ValueError('ProCredit transfer TAN must contain exactly 4 digits')
