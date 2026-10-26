"""No network or real transfers: mocked REST responses only."""

from decimal import Decimal

import pytest
import requests

from api.parabank_api import ApiTransferData, ParaBankApi, _demo_api_url


class FakeResponse:
    def __init__(self, payload=None, status_code=200):
        self.payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append(("GET", url, kwargs))
        return self.responses.pop(0)

    def post(self, url, **kwargs):
        self.calls.append(("POST", url, kwargs))
        return self.responses.pop(0)


def test_get_returns_exact_decimal_balance():
    session = FakeSession([FakeResponse({"id": 12345, "balance": 99.10})])
    client = ParaBankApi(base_url="http://localhost:8081/parabank/services/bank", session=session)
    assert client.get_account_balance("12345") == Decimal("99.10")
    method, url, kwargs = session.calls[0]
    assert method == "GET" and url.endswith("/accounts/12345")
    assert kwargs["headers"]["Accept"] == "application/json"
    assert kwargs["timeout"] == 15


def test_post_uses_query_params_not_json_body():
    session = FakeSession([FakeResponse("Successfully transferred")])
    client = ParaBankApi(base_url="http://localhost:8081/parabank/services/bank", session=session)
    data = ApiTransferData("11111", "22222", Decimal("1.00"))
    assert client.post_transfer(data).status_code == 200
    method, url, kwargs = session.calls[0]
    assert method == "POST" and url.endswith("/transfer")
    assert kwargs["params"] == {
        "fromAccountId": "11111", "toAccountId": "22222", "amount": "1.00"
    }
    assert "json" not in kwargs and "data" not in kwargs


def test_balance_validation_detects_wrong_debit():
    with pytest.raises(AssertionError, match="Sender balance"):
        ParaBankApi.verify_balance_changes(
            Decimal("10"), Decimal("5"), Decimal("10"), Decimal("6"), Decimal("1")
        )


def test_balance_validation_detects_wrong_credit():
    with pytest.raises(AssertionError, match="Receiver balance"):
        ParaBankApi.verify_balance_changes(
            Decimal("10"), Decimal("5"), Decimal("9"), Decimal("5"), Decimal("1")
        )


def test_parse_environment_validates_demo_accounts(monkeypatch):
    monkeypatch.setenv("PARABANK_FROM_ACCOUNT", "12345")
    monkeypatch.setenv("PARABANK_TO_ACCOUNT", "98765")
    monkeypatch.setenv("PARABANK_TRANSFER_AMOUNT", "1.25")
    assert ApiTransferData.from_environment().amount == Decimal("1.25")
    monkeypatch.setenv("PARABANK_TO_ACCOUNT", "12345")
    with pytest.raises(ValueError, match="differ"):
        ApiTransferData.from_environment()


def test_transfer_amount_rejects_invalid_input(monkeypatch):
    monkeypatch.setenv("PARABANK_FROM_ACCOUNT", "12345")
    monkeypatch.setenv("PARABANK_TO_ACCOUNT", "98765")
    for value in ("-1", "0", "1.234", "NaN", "Infinity"):
        monkeypatch.setenv("PARABANK_TRANSFER_AMOUNT", value)
        with pytest.raises(ValueError):
            ApiTransferData.from_environment()


def test_default_api_uses_existing_local_parabank_port(monkeypatch):
    monkeypatch.delenv("PARABANK_BASE_URL", raising=False)
    monkeypatch.delenv("PARABANK_API_BASE_URL", raising=False)
    assert _demo_api_url() == "http://localhost:8081/parabank/services/bank"


def test_unapproved_external_hosts_rejected():
    with pytest.raises(ValueError, match="Only localhost"):
        ParaBankApi(base_url="https://online.procreditbank.ge/parabank/services/bank")


def test_public_demo_requires_explicit_opt_in(monkeypatch):
    monkeypatch.delenv("PARABANK_API_ALLOW_PUBLIC", raising=False)
    with pytest.raises(ValueError, match="PARABANK_API_ALLOW_PUBLIC"):
        ParaBankApi(base_url="https://parabank.parasoft.com/parabank/services/bank")


def test_get_rejects_unexpected_account():
    client = ParaBankApi(
        base_url="http://localhost:8081/parabank/services/bank",
        session=FakeSession([FakeResponse({"id": 99999, "balance": 100})]),
    )
    with pytest.raises(AssertionError, match="different account"):
        client.get_account_balance("12345")


def test_get_propagates_http_errors():
    client = ParaBankApi(
        base_url="http://localhost:8081/parabank/services/bank",
        session=FakeSession([FakeResponse(status_code=404)]),
    )
    with pytest.raises(requests.HTTPError):
        client.get_account_balance("12345")
