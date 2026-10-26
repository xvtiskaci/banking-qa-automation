import os
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from urllib.parse import urlsplit

import requests

from utils.ParserUtils import ParserUtils


@dataclass(frozen=True)
class ApiTransferData:
    from_account_id: str
    to_account_id: str
    amount: Decimal

    @classmethod
    def from_environment(cls):
        sender = os.getenv("PARABANK_FROM_ACCOUNT", "").strip()
        receiver = os.getenv("PARABANK_TO_ACCOUNT", "").strip()
        amount_text = os.getenv("PARABANK_TRANSFER_AMOUNT", "1.00").strip()

        if not sender or not receiver:
            raise ValueError("Set PARABANK_FROM_ACCOUNT and PARABANK_TO_ACCOUNT (demo account IDs).")
        if not sender.isascii() or not sender.isdecimal() or not receiver.isascii() or not receiver.isdecimal():
            raise ValueError("ParaBank account IDs must contain ASCII digits only.")
        if sender == receiver:
            raise ValueError("Source and destination accounts must differ.")
        if not re.fullmatch(r"\d+(?:\.\d{1,2})?", amount_text):
            raise ValueError("PARABANK_TRANSFER_AMOUNT must have at most two decimal places.")
        amount = Decimal(amount_text)
        if amount <= 0:
            raise ValueError("PARABANK_TRANSFER_AMOUNT must be greater than zero.")

        return cls(sender, receiver, amount)


def _demo_api_url():
    configured_web_url = ParserUtils.parse_json("config.json")["urls"]["parabank"]
    web_url = os.getenv("PARABANK_BASE_URL", configured_web_url).rstrip("/")
    api_url = os.getenv("PARABANK_API_BASE_URL", f"{web_url}/services/bank").rstrip("/")
    parsed = urlsplit(api_url)

    allowed_local = {"localhost", "127.0.0.1", "::1"}
    if parsed.scheme not in {"http", "https"} or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("Invalid ParaBank API URL.")
    if parsed.hostname not in allowed_local | {"parabank.parasoft.com"}:
        raise ValueError("API transfers are restricted to localhost or ParaBank's official demo host.")
    if not parsed.path.endswith("/parabank/services/bank"):
        raise ValueError("API URL must end in /parabank/services/bank.")
    if parsed.hostname == "parabank.parasoft.com":
        if parsed.scheme != "https" or os.getenv("PARABANK_API_ALLOW_PUBLIC") != "YES":
            raise ValueError("Public ParaBank demo requires HTTPS and PARABANK_API_ALLOW_PUBLIC=YES.")
    return api_url


class ParaBankApi:

    def __init__(self, base_url=None, session=None, timeout=15):
        self.base_url = self._validate_url(base_url) if base_url else _demo_api_url()
        self.session = session if session is not None else requests.Session()
        self.timeout = timeout

    @staticmethod
    def _validate_url(url):
        parsed = urlsplit(url)
        if parsed.scheme not in {"http",
                                 "https"} or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("Invalid ParaBank API URL.")
        if parsed.hostname not in {"localhost", "127.0.0.1", "::1", "parabank.parasoft.com"}:
            raise ValueError("Only localhost and ParaBank's official demo are allowed.")
        if not parsed.path.rstrip("/").endswith("/parabank/services/bank"):
            raise ValueError("Expected /parabank/services/bank URL suffix.")
        if parsed.hostname == "parabank.parasoft.com":
            if parsed.scheme != "https" or os.getenv("PARABANK_API_ALLOW_PUBLIC") != "YES":
                raise ValueError("Set PARABANK_API_ALLOW_PUBLIC=YES to use the public demo.")
        return url.rstrip("/")

    def get_account_balance(self, account_id):
        response = self.session.get(
            f"{self.base_url}/accounts/{account_id}",
            headers={"Accept": "application/json"}, timeout=self.timeout,
        )
        response.raise_for_status()
        assert response.status_code == 200, f"GET account HTTP {response.status_code}"
        payload = response.json()
        assert isinstance(payload, dict), "GET account must return a JSON object"
        assert str(payload.get("id")) == str(int(account_id)), "GET returned a different account"
        try:
            balance = Decimal(str(payload["balance"]))
        except (KeyError, InvalidOperation, TypeError, ValueError) as exc:
            raise AssertionError("GET account response contains no valid balance") from exc
        assert balance.is_finite(), "Account balance must be finite"
        return balance

    def post_transfer(self, data):
        response = self.session.post(
            f"{self.base_url}/transfer",
            params={
                "fromAccountId": data.from_account_id,
                "toAccountId": data.to_account_id,
                "amount": f"{data.amount:.2f}",
            },
            headers={"Accept": "application/json"}, timeout=self.timeout,
        )
        response.raise_for_status()
        assert response.status_code == 200, f"POST transfer HTTP {response.status_code}"
        return response

    @staticmethod
    def verify_balance_changes(before_sender, before_receiver, after_sender, after_receiver, amount):
        assert after_sender == before_sender - amount, (
            f"Sender balance: expected {before_sender - amount}, got {after_sender}"
        )
        assert after_receiver == before_receiver + amount, (
            f"Receiver balance: expected {before_receiver + amount}, got {after_receiver}"
        )
