import allure
import pytest

from steps.procreditbank_mobile_negative_transfer_steps import ProcreditMobileNegativeTransferSteps


@pytest.mark.site("procreditbank")
@pytest.mark.procredit_mobile
@pytest.mark.livebank
@allure.epic("ProCredit Bank — Mobile")
@allure.feature("Domestic Payment")
class TestProcreditMobileNegativeTransfer:

    @allure.title("Mobile — Insufficient Funds Negative Transfer")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_mobile_negative_transfer(self):
        ProcreditMobileNegativeTransferSteps.mobile_negative_transfer_steps()
