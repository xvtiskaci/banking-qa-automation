"""Offline regression tests of login OTP and transfer TAN parsing."""
from pathlib import Path

import pytest

from utils.AndroidSmsOtpProvider import AndroidSmsOtpProvider


def make_provider():
    return AndroidSmsOtpProvider('test_user', 'ProCredit', code_length=4, ssh_key=Path('unused'))


@pytest.mark.unit
def test_login_code_is_extracted_using_label(monkeypatch):
    provider = make_provider()
    monkeypatch.setattr(AndroidSmsOtpProvider, '_read_messages', lambda self: [
        {'_id': 'old', 'number': 'ProCredit', 'body': 'code: 9876. earlier login'},
        {'_id': 'new', 'number': 'ProCredit',
         'body': 'code: 1234. confirm you entered the code\nreference QWERTY'},
    ])
    assert provider.wait_for_new_code({'old'}, timeout=0.1, interval=0.001,
                                      purpose='login') == '1234'


@pytest.mark.unit
def test_transfer_tan_ignores_four_digit_account_suffix(monkeypatch):
    provider = make_provider()
    monkeypatch.setattr(AndroidSmsOtpProvider, '_read_messages', lambda self: [
        {'_id': 'old', 'number': 'ProCredit', 'body': 'TAN CODE: 9999\naccount: **** 8888'},
        {'_id': 'new', 'number': 'ProCredit',
         'body': 'TAN CODE: 4321\nTanxa: 11\nangarishi: **** 7654 GEL\nref X123'},
    ])
    assert provider.wait_for_new_code({'old'}, timeout=0.1, interval=0.001,
                                      purpose='transfer') == '4321'


@pytest.mark.unit
def test_login_does_not_accept_transfer_tan(monkeypatch):
    provider = make_provider()
    monkeypatch.setattr(AndroidSmsOtpProvider, '_read_messages', lambda self: [
        {'_id': 'new', 'number': 'ProCredit',
         'body': 'TAN CODE: 4321\naccount: **** 7654 GEL'},
    ])
    with pytest.raises(TimeoutError, match='No fresh labelled SMS'):
        provider.wait_for_new_code(set(), timeout=0.004, interval=0.001, purpose='login')


@pytest.mark.unit
def test_transfer_does_not_accept_login_code(monkeypatch):
    provider = make_provider()
    monkeypatch.setattr(AndroidSmsOtpProvider, '_read_messages', lambda self: [
        {'_id': 'new', 'number': 'ProCredit', 'body': 'code: 1234.'},
    ])
    with pytest.raises(TimeoutError, match='No fresh labelled SMS'):
        provider.wait_for_new_code(set(), timeout=0.004, interval=0.001,
                                   purpose='transfer')


@pytest.mark.unit
def test_stale_or_wrong_sender_sms_cannot_satisfy_wait(monkeypatch):
    provider = make_provider()
    monkeypatch.setattr(AndroidSmsOtpProvider, '_read_messages', lambda self: [
        {'_id': 'old', 'number': 'ProCredit', 'body': 'TAN CODE: 4321'},
        {'_id': 'new', 'number': 'AnotherBank', 'body': 'TAN CODE: 1234'},
    ])
    with pytest.raises(TimeoutError, match='No fresh labelled SMS'):
        provider.wait_for_new_code({'old'}, timeout=0.004, interval=0.001,
                                   purpose='transfer')


@pytest.mark.unit
def test_reject_unlabelled_four_digits(monkeypatch):
    provider = make_provider()
    monkeypatch.setattr(AndroidSmsOtpProvider, '_read_messages', lambda self: [
        {'_id': 'new', 'number': 'ProCredit', 'body': 'account: **** 7654, amount 11'},
    ])
    with pytest.raises(TimeoutError, match='No fresh labelled SMS'):
        provider.wait_for_new_code(set(), timeout=0.004, interval=0.001,
                                   purpose='transfer')


@pytest.mark.unit
def test_invalid_purpose_fails_fast():
    with pytest.raises(ValueError, match='purpose'):
        make_provider().wait_for_new_code(set(), purpose='other')
