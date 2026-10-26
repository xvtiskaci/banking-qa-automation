import pytest
import allure

from steps.smoke_steps import SmokeSteps


@pytest.mark.site("parabank")
@allure.epic("ParaBank Demo")
@allure.feature("ავტორიზაცის და აქაუნთის Overview")
@allure.story("Safe smoke test გადარიცხვების გარეშე")
class TestParaBankSmoke:
    @allure.title("Smoke — ავტორიზაცია და ანგარიშების მიმოხილვა")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_and_accounts_overview(self):
        SmokeSteps.login_and_verify_accounts()
