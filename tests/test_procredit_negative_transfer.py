import pytest
import allure

from steps.procreditbank_negative_transfer_steps import ProcreditNegativeTransferSteps


@pytest.mark.site("procreditbank")
@pytest.mark.livebank
@allure.epic("ProCredit Bank Internet Banking")
@allure.feature("Domestic Payment")
class TestProcreditNegativeTransfer:

    @allure.title("Insufficient Funds Negative Transfer")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_insufficient_funds(self):
        ProcreditNegativeTransferSteps.negative_transfer_steps()