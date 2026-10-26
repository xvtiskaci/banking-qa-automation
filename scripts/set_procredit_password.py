import getpass
import os
import sys

from data.models.data_for_procreditbank import DataForProcreditBank


def main():
    DataForProcreditBank.configure()
    username = os.getenv("PRO_CREDIT_USERNAME", "").strip()
    if not username or username.upper().startswith("YOUR_"):
        raise SystemExit("First fill PRO_CREDIT_USERNAME in your local .env file.")

    try:
        import keyring
    except ImportError:
        raise SystemExit("Install once: python -m pip install -r requirements-procredit-config.txt")

    first = getpass.getpass("ProCredit password (hidden): ")
    second = getpass.getpass("Repeat password (hidden): ")
    if not first or first != second:
        raise SystemExit("Passwords were empty or different. Nothing was saved.")
    try:
        keyring.set_password(DataForProcreditBank.CREDENTIAL_SERVICE, username, first)
    except Exception as exc:
        raise SystemExit(f"Credential Manager save failed: {type(exc).__name__}") from exc
    finally:
        del first, second

    print("Password saved in the local system credential store for this login.")
    print("It will be loaded automatically when pytest starts (no bank secrets in source).")


if __name__ == "__main__":
    main()
