import os
import re
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ProcreditTestData:
    recipient_iban: str
    recipient_name: str
    expected_bank_name: str

    @classmethod
    def from_environment(cls):
        iban = os.getenv('PRO_CREDIT_RECIPIENT_IBAN', '').strip().upper().replace(' ', '')
        recipient = os.getenv('PRO_CREDIT_RECIPIENT_NAME', '').strip()
        expected = os.getenv('PRO_CREDIT_EXPECTED_BANK_NAME', 'სს "თიბისი ბანკი"').strip()
        if not re.fullmatch(r'GE\d{2}[A-Z]{2}\d{16}', iban):
            raise ValueError('PRO_CREDIT_RECIPIENT_IBAN must be a valid-format Georgian IBAN (22 chars)')
        if not recipient:
            raise ValueError('Set PRO_CREDIT_RECIPIENT_NAME in your local environment')
        if not expected:
            raise ValueError('Set PRO_CREDIT_EXPECTED_BANK_NAME in your local environment')
        return cls(iban, recipient, expected)


@dataclass(frozen=True)
class PreparedInvalidTransfer:
    available_balance: Decimal
    requested_amount: Decimal

