import os
import pytest
import allure
from steps.procreditbank_login_page_steps import LoginPageSteps


@pytest.mark.site('procreditbank')
@pytest.mark.skipif(os.getenv('PRO_CREDIT_RUN') != '1', reason='Set PRO_CREDIT_RUN=1 to run live login')
@allure.epic('ProCredit Bank Internet Banking')
class TestLogin:
    def test_procredit_login(self):
        LoginPageSteps.login_page_steps()
