import allure

from steps.procreditbank_negative_transfer_steps import ProcreditNegativeTransferSteps


class ProcreditMobileNegativeTransferSteps:
    @staticmethod
    def mobile_negative_transfer_steps():
        with allure.step('Mobile 414×896 — სრული Negative Transfer სცენარი'):
            ProcreditNegativeTransferSteps.negative_transfer_steps(mobile=True)
