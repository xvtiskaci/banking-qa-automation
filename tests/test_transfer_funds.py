import pytest
import allure

from steps.transfer_funds_steps import TransferFundsSteps


@pytest.mark.site("parabank")
@allure.epic("ParaBank Demo")
@allure.feature("Internal Funds Transfer")
@allure.story("Transfer between user's own accounts")
class TestTransferFunds:
    @allure.title("შიდა გადარიცხვა — ბალანსები და Debit/Credit ისტორია")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_successful_internal_transfer(self):
        TransferFundsSteps.successful_transfer()
