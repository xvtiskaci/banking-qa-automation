import os
from pathlib import Path

from dotenv import load_dotenv


class DataForProcreditBank:
    ROOT = Path(__file__).resolve().parents[2]
    CREDENTIAL_SERVICE = "ProCreditBankAutomation"
    DEFAULTS = {
        "PRO_CREDIT_RUN": "0",
        "PRO_CREDIT_NEGATIVE_SUBMIT": "NO",
        "PRO_CREDIT_MOBILE_NEGATIVE_SUBMIT": "NO",
        "PRO_CREDIT_MANUAL_WARNING_CHECK": "0",
        "PROCREDIT_OTP_LENGTH": "4",
        "HEADLESS": "false",
        "BROWSER": "chrome",
        "PRO_CREDIT_EXPECTED_BANK_NAME": 'სს "თიბისი ბანკი"',
    }

    @staticmethod
    def configure(env_path=None):
        path = Path(env_path) if env_path is not None else DataForProcreditBank.ROOT / ".env"
        load_dotenv(dotenv_path=path, encoding="utf-8", override=False)

        for name, value in DataForProcreditBank.DEFAULTS.items():
            os.environ.setdefault(name, value)

        if os.environ.get("PRO_CREDIT_PASSWORD"):
            return
        username = os.environ.get("PRO_CREDIT_USERNAME", "").strip()
        if not username or username.upper().startswith("YOUR_"):
            return

        try:
            import keyring
            password = keyring.get_password(DataForProcreditBank.CREDENTIAL_SERVICE, username)
        except Exception:
            return
        if password:
            os.environ["PRO_CREDIT_PASSWORD"] = password
