import os

import allure
import pytest

from steps.procreditbank_mobile_login_steps import ProcreditMobileLoginSteps


@pytest.mark.site('procreditbank')
@pytest.mark.procredit_mobile
@pytest.mark.skipif(os.getenv('PRO_CREDIT_RUN') != '1', reason='Set PRO_CREDIT_RUN=1 for live login')
@allure.epic('ProCredit Bank Internet Banking — Mobile Responsive')
class TestProcreditMobileLogin:
    @allure.title('Mobile 414x896 — SMS OTP login')
    def test_mobile_login(self):
        ProcreditMobileLoginSteps.mobile_login_steps()
