import os
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


@dataclass(frozen=True)
class TransferTestData:
    username: str
    password: str
    from_account_id: str
    to_account_id: str
    amount: Decimal

    @classmethod
    def from_environment(cls):
        keys = (
            "PARABANK_USERNAME", "PARABANK_PASSWORD",
            "PARABANK_FROM_ACCOUNT", "PARABANK_TO_ACCOUNT",
            "PARABANK_TRANSFER_AMOUNT",
        )
        values = {key: os.getenv(key, "") for key in keys}
        for key in keys:
            if key != "PARABANK_PASSWORD":
                values[key] = values[key].strip()
        missing = [key for key, value in values.items() if not value]
        if missing:
            raise ValueError("Missing environment variables: " + ", ".join(missing))

        try:
            amount = Decimal(values["PARABANK_TRANSFER_AMOUNT"])
        except InvalidOperation as exc:
            raise ValueError("PARABANK_TRANSFER_AMOUNT must be numeric") from exc

        if not amount.is_finite() or amount <= 0:
            raise ValueError("Transfer amount must be a positive finite number")
        if amount.as_tuple().exponent < -2:
            raise ValueError("Transfer amount must have at most 2 decimal places")
        if values["PARABANK_FROM_ACCOUNT"] == values["PARABANK_TO_ACCOUNT"]:
            raise ValueError("From and To account IDs must be different")

        return cls(
            username=values["PARABANK_USERNAME"],
            password=values["PARABANK_PASSWORD"],
            from_account_id=values["PARABANK_FROM_ACCOUNT"],
            to_account_id=values["PARABANK_TO_ACCOUNT"],
            amount=amount,
        )
