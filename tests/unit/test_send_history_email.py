import datetime

import pytest

from src.account import PersonalAccount, CompanyAccount


@pytest.fixture
def fixed_today():
    # Capture today's date once for deterministic subject assertions.
    return datetime.datetime.now().strftime("%Y-%m-%d")


def _assert_send_called(smtp_instance, expected_text, expected_email, expected_date):
    smtp_instance.send.assert_called_once()
    subject_arg, text_arg, email_arg = smtp_instance.send.call_args[0]
    assert subject_arg == f"Account Transfer History {expected_date}"
    assert text_arg == expected_text
    assert email_arg == expected_email


def test_send_history_personal_success(mocker, fixed_today):
    account = PersonalAccount("John", "Doe", "12345678901")
    account.history = [100.0, -50.0]

    smtp_mock = mocker.patch("src.account.SMTPClient")
    smtp_instance = smtp_mock.return_value
    smtp_instance.send.return_value = True

    result = account.send_history_via_email("user@example.com")

    assert result is True
    _assert_send_called(
        smtp_instance,
        "Personal account history: [100.0, -50.0]",
        "user@example.com",
        fixed_today,
    )


def test_send_history_personal_failure(mocker, fixed_today):
    account = PersonalAccount("Jane", "Doe", "12345678901")
    account.history = [10.0]

    smtp_mock = mocker.patch("src.account.SMTPClient")
    smtp_instance = smtp_mock.return_value
    smtp_instance.send.return_value = False

    result = account.send_history_via_email("user@example.com")

    assert result is False
    _assert_send_called(
        smtp_instance,
        "Personal account history: [10.0]",
        "user@example.com",
        fixed_today,
    )


def test_send_history_company_success(mocker, fixed_today):
    mocker.patch.object(CompanyAccount, "check_vat_status", return_value=True)
    account = CompanyAccount("ACME", "1234567890")
    account.history = [500.0, -200.0]

    smtp_mock = mocker.patch("src.account.SMTPClient")
    smtp_instance = smtp_mock.return_value
    smtp_instance.send.return_value = True

    result = account.send_history_via_email("corp@example.com")

    assert result is True
    _assert_send_called(
        smtp_instance,
        "Company account history: [500.0, -200.0]",
        "corp@example.com",
        fixed_today,
    )


def test_send_history_company_failure(mocker, fixed_today):
    mocker.patch.object(CompanyAccount, "check_vat_status", return_value=True)
    account = CompanyAccount("ACME", "1234567890")
    account.history = [1.0]

    smtp_mock = mocker.patch("src.account.SMTPClient")
    smtp_instance = smtp_mock.return_value
    smtp_instance.send.return_value = False

    result = account.send_history_via_email("corp@example.com")

    assert result is False
    _assert_send_called(
        smtp_instance,
        "Company account history: [1.0]",
        "corp@example.com",
        fixed_today,
    )
