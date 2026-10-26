"""Offline checks only; do not open the browser or bank website."""
import os
import sys
from types import SimpleNamespace

from data.models.data_for_procreditbank import DataForProcreditBank


def test_env_file_loaded_and_safe_defaults(monkeypatch, tmp_path):
    path = tmp_path / '.env'
    path.write_text('PRO_CREDIT_RUN=1\nPROCREDIT_OTP_LENGTH=4\nPRO_CREDIT_USERNAME=YOUR_BANK_LOGIN\n',encoding='utf-8')
    for key in ('PRO_CREDIT_RUN', 'PROCREDIT_OTP_LENGTH', 'PRO_CREDIT_NEGATIVE_SUBMIT',
                'PRO_CREDIT_USERNAME', 'PRO_CREDIT_PASSWORD'):
        monkeypatch.delenv(key,raising=False)
    DataForProcreditBank.configure(env_path=path)
    assert os.getenv('PRO_CREDIT_RUN') == '1'
    assert os.getenv('PROCREDIT_OTP_LENGTH') == '4'
    assert os.getenv('PRO_CREDIT_NEGATIVE_SUBMIT') == 'NO'


def test_existing_run_configuration_overrides_dotenv(monkeypatch, tmp_path):
    path = tmp_path / '.env'
    path.write_text('PRO_CREDIT_RUN=1\n',encoding='utf-8')
    monkeypatch.setenv('PRO_CREDIT_RUN','0')
    monkeypatch.setenv('PRO_CREDIT_PASSWORD','already-from-process')
    DataForProcreditBank.configure(env_path=path)
    assert os.getenv('PRO_CREDIT_RUN') == '0'
    assert os.getenv('PRO_CREDIT_PASSWORD') == 'already-from-process'


def test_password_is_fetched_from_credential_store(monkeypatch, tmp_path):
    path = tmp_path / '.env'
    path.write_text('PRO_CREDIT_USERNAME=examplelogin\n',encoding='utf-8')
    monkeypatch.delenv('PRO_CREDIT_USERNAME',raising=False)
    monkeypatch.delenv('PRO_CREDIT_PASSWORD',raising=False)
    record = []
    def get_password(service, username):
        record.append((service, username))
        return 'test-only-password'
    monkeypatch.setitem(sys.modules, 'keyring', SimpleNamespace(get_password=get_password))
    DataForProcreditBank.configure(env_path=path)
    assert record == [('ProCreditBankAutomation','examplelogin')]
    assert os.getenv('PRO_CREDIT_PASSWORD') == 'test-only-password'


def test_no_saved_password_does_not_crash_test_collection(monkeypatch, tmp_path):
    path = tmp_path / '.env'
    path.write_text('PRO_CREDIT_USERNAME=YOUR_LOGIN\n',encoding='utf-8')
    monkeypatch.delenv('PRO_CREDIT_USERNAME',raising=False)
    monkeypatch.delenv('PRO_CREDIT_PASSWORD',raising=False)
    DataForProcreditBank.configure(env_path=path)
    assert not os.getenv('PRO_CREDIT_PASSWORD')
