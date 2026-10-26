
import allure

from api.parabank_api import ApiTransferData, ParaBankApi


class ParaBankApiTransferSteps:
    @staticmethod
    def successful_transfer():
        data = ApiTransferData.from_environment()
        api = ParaBankApi()

        with allure.step("1. GET: ორივე დემო ანგარიშის საწყისი ბალანსის წამოღება"):
            sender_before = api.get_account_balance(data.from_account_id)
            receiver_before = api.get_account_balance(data.to_account_id)
            assert sender_before >= data.amount, "Demo sender account has insufficient balance"

        with allure.step("2. POST: ParaBank დემო გადარიცხვა (query parameters)"):
            api.post_transfer(data)

        with allure.step("3. GET: ორივე ანგარიშის საბოლოო ბალანსის წამოღება"):
            sender_after = api.get_account_balance(data.from_account_id)
            receiver_after = api.get_account_balance(data.to_account_id)

        with allure.step("4. Assert: თანხა სწორად ჩამოიჭრა და ჩაირიცხა"):
            api.verify_balance_changes(
                sender_before, receiver_before,
                sender_after, receiver_after, data.amount,
            )
            allure.attach(
                f"Sender: {sender_before} -> {sender_after}\n"
                f"Receiver: {receiver_before} -> {receiver_after}\n"
                f"Transferred: {data.amount:.2f}",
                name="Demo API balance validation",
                attachment_type=allure.attachment_type.TEXT,
            )
