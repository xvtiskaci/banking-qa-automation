import os

import allure
import pytest

from steps.parabank_api_transfer_steps import ParaBankApiTransferSteps


@pytest.mark.api
@allure.epic("ParaBank Demo REST API")
@allure.feature("GET → POST → GET Internal Transfer")
@allure.story("Demo transfer with balance validation")
class TestParaBankApiTransfer:
    @pytest.mark.skipif(
        os.getenv("PARABANK_API_TRANSFER_RUN") != "YES",
        reason="Demo POST transfer is off; set PARABANK_API_TRANSFER_RUN=YES explicitly",
    )
    @allure.title("API: GET balances → POST transfer → GET balances")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_successful_transfer_via_api(self):
        ParaBankApiTransferSteps.successful_transfer()
