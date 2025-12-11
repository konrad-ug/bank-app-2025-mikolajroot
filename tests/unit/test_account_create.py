from symtable import Class

import pytest

from src.account import PersonalAccount, Account, AccountRegistry
from src.account import CompanyAccount



class TestAccount:
    def test_account_creation(self):
        account = PersonalAccount("John", "Doe", '134321346542')
        assert account.first_name == "John"
        assert account.last_name == "Doe"
        assert account.balance == 0.0
        assert account.pesel == 'Invalid'

    def test_pesel_too_long(self):
        account = PersonalAccount("Jane", "Doe", '4234324342424234')
        assert account.pesel == 'Invalid'

    def test_pesel_too_short(self):
        account = PersonalAccount("Jane", "Doe", '871368')
        assert account.pesel == 'Invalid'

    def test_pesel_empty(self):
        account = PersonalAccount("Jane", "Doe", '')
        assert account.pesel == 'Invalid'

    def test_too_long_promoCode(self):
        account = PersonalAccount("Jane", "Doe", '', 'PROM_1234')
        assert account.balance == 0.0

    def test_too_short_promoCode(self):
        account = PersonalAccount("Jane", "Doe", '', 'PROM_12')
        assert account.balance == 0.0

    def test_bad_promoCode(self):
        account = PersonalAccount("Jane", "Doe", '', 'PROM-123')
        assert account.balance == 0.0

    def test_to_old(self):
        account = PersonalAccount("Jane", "Doe", '55232465786', 'PROM_123')
        assert account.balance == 0.0

    def test_young(self):
        account = PersonalAccount("Jane", "Doe", '62232465786', 'PROM_123')
        assert account.balance == 50.0

    def test_transfer_in(self):
        account = PersonalAccount("Jane", "Doe", '62232465786', 'PROM_123')
        assert account.balance == 50.0
        account.transfer_in(50.0)
        assert account.balance == 100.0

    def test_correct_transfer_out(self):
        account = PersonalAccount("Jane", "Doe", '62232465786', 'PROM_123')
        assert account.balance == 50.0
        account.transfer_out(20.0)
        assert account.balance == 30.0

    def test_too_low_balance_transfer_out(self):
        account = PersonalAccount("Jane", "Doe", '62232465786', 'PROM-123')
        assert account.balance == 0
        account.transfer_out(20.0)
        assert account.balance == 0

    def test_express_transfer_out(self):
        account = PersonalAccount("Jane", "Doe", '62232465786', 'PROM-123')
        account.balance = 50.0

        account.express_transfer_out(30.0)

        assert account.balance == 19.0

    def test_express_negative_transfer_out(self):
        account = PersonalAccount("Jane", "Doe", '62232465786', 'PROM-123')
        account.balance = 50.0

        account.express_transfer_out(50.0)

        assert account.balance == -1.0

    def test_express_too_low_balance_transfer_out(self):
        account = PersonalAccount("Jane", "Doe", '62232465786', 'PROM-123')
        account.balance = 50.0

        account.express_transfer_out(60)

        assert account.balance == 50.0


class TestCompanyAccount:

    @pytest.fixture(autouse=True)
    def mock_api_calls(self, mocker):
        mock_response = mocker.Mock()
        mock_response.json.return_value = {
            "result": {
                "subject": {
                    "statusVat": "Czynny"
                }
            }
        }
        mock_response.status_code = 200

        return mocker.patch("src.account.requests.get", return_value=mock_response)


    def test_account_creation(self):
        account = CompanyAccount('nazwa_firmy', '1343213465')
        assert account.company_name == 'nazwa_firmy'
        assert account.nip == '1343213465'

    def test_nip_too_long(self):
        account = CompanyAccount('nazwa_firmy', '13432134654')
        assert account.nip == 'Invalid'

    def test_nip_too_short(self):
        account = CompanyAccount('nazwa_firmy', '1343')
        assert account.nip == 'Invalid'

    def test_nip_empty(self):
        account = CompanyAccount('nazwa_firmy', '')
        assert account.nip == 'Invalid'

    def test_transfer_in(self):
        account = CompanyAccount('nazwa_firmy', '1343213465')
        account.balance = 50.0

        account.transfer_in(100.0)

        assert account.balance == 150.0

    def test_correct_transfer_out(self):
        account = CompanyAccount('nazwa_firmy', '1343213465')
        account.balance = 50.0

        account.transfer_out(20.0)

        assert account.balance == 30.0

    def test_too_low_balance_transfer_out(self):
        account = CompanyAccount('nazwa_firmy', '1343213465')
        account.balance = 50.0

        account.transfer_out(100.0)

        assert account.balance == 50.0

    def test_negative_number_transfer_out(self):
        account = CompanyAccount('nazwa_firmy', '1343213465')
        account.balance = 50.0

        account.transfer_out(-30.0)

        assert account.balance == 50.0

    def test_express_transfer_out(self):
        account = CompanyAccount('nazwa_firmy', '1343213465')
        account.balance = 50.0

        account.express_transfer_out(30.0)

        assert account.balance == 15.0

    def test_express_negative_transfer_out(self):
        account = CompanyAccount('nazwa_firmy', '1343213465')
        account.balance = 50.0

        account.express_transfer_out(50.0)

        assert account.balance == -5.0

    def test_express_too_low_balance_transfer_out(self):
        account = CompanyAccount('nazwa_firmy', '1343213465')
        account.balance = 50.0

        account.express_transfer_out(60)

        assert account.balance == 50.0

    def test_check_balance(self):
        account = Account()

        assert account.balance == 0.0
        assert account.history == []

    def test_check_history_transfer_out(self):
        account = CompanyAccount('nazwa_firmy', '1343213465')

        account.balance = 50.0

        account.transfer_out(30)

        assert account.history == [-30]

    def test_check_express_history_transfer_out(self):
        account = CompanyAccount('nazwa_firmy', '1343213465')

        account.balance = 500.0

        account.express_transfer_out(51)
        assert account.history == [-51, -5.0]

    @pytest.fixture()
    def personalAccount(self):
        account = PersonalAccount("Jane", "Doe", '62232465786')
        return account

    @pytest.mark.parametrize("initial_balance, transactions, loan_amount, expected_result, expected_balance", [

        # test_submit_for_loan
        (50.0, [('in', 100), ('in', 100), ('in', 100), ('in', 100), ('in', 100)], 200, True, 750.0),

        # test_submit_for_loan_too_little_transactions
        (50.0, [('in', 10), ('in', 10)], 200, False, 70.0),

        # test_submit_for_loan_last_three_not_transfer_in
        (100.0, [('in', 10), ('in', 10), ('in', 10), ('in', 1000), ('out', -100)], 200, True, 1330.0),

        (100.0, [('in', 1000), ('in', 1000), ('in', 1000), ('in', 1000), ('out', 100)], 2000, True, 6000.0),

        # test_submit_for_loan_two_conditions_not_met
        (100.0, [('in', 10), ('in', 10), ('in', 10), ('in', 10), ('out', 10)], 50, False, 130.0)
    ])
    def test_submit_for_loan_parameterized(self, personalAccount, initial_balance, transactions, loan_amount,
                                           expected_result,
                                           expected_balance):
        personalAccount.balance = initial_balance

        for type, amount in transactions:
            if type == 'in':
                personalAccount.transfer_in(amount)
            elif type == 'out':
                personalAccount.transfer_out(amount)

        result = personalAccount.submit_for_loan(loan_amount)

        assert result == expected_result
        assert personalAccount.balance == expected_balance

    def test_last_three_transfer_out(self, personalAccount):
        personalAccount.balance = 100

        personalAccount.transfer_out(10)
        personalAccount.transfer_in(20)
        personalAccount.transfer_in(20)

        assert personalAccount.last_three_tranfer_in() == False

    @pytest.fixture()
    def companyAccount(self):
        account = CompanyAccount('nazwa_firmy', '1343213465')
        return account

    @pytest.mark.parametrize("initial_balance, history, loan_amount, expected_result, expected_balance", [

        # test_submit_for_loan
        (2000, [-1775], 200, True, 2200),

        # test_submit_for_loan_balance_too_small
        (2000, [-1775], 2000, False, 2000),

        # test_submit_for_loan_no_zus_transfer
        (2000, [123,40], 200, False, 2000),

    ])
    def test_submit_for_loan_company_parameterized(self, companyAccount, initial_balance, history, loan_amount,
                                                   expected_result,
                                                   expected_balance):
        companyAccount.balance = initial_balance

        companyAccount.history = history

        result = companyAccount.submit_for_loan(loan_amount)

        assert result == expected_result
        assert companyAccount.balance == expected_balance

    def test_constructor_raises_error_if_company_not_registered(self, mock_api_calls):
        mock_api_calls.return_value.json.return_value = {
            "result": {
                "subject": {
                    "statusVat": "Nieczynny"
                }
            }
        }
        with pytest.raises(ValueError, match="Company not registered!!"):
            CompanyAccount('kjandfna', '1234567890')

class TestRegistry:
    @pytest.fixture()
    def registry(self):
        registry = AccountRegistry()
        return registry

    def test_creating_registry(self,registry):
        assert registry.accounts == []

    def test_adding_account(self,registry,personalAccount):

        account = personalAccount

        registry.add_account(account)

        assert registry.accounts[0] == account

    @pytest.mark.parametrize("pesel, should_find", [
        # test_good_pesel
        ("62232465786", True),

        # test_bad_pesel_too_short
        ("6223246578", False),

        # test_good_pesel_but_different
        ("00000000000", False),

        # test_empty_string
        ("", False)
    ])
    def test_search_good_pesel(self,registry,personalAccount,pesel,should_find):
        account = personalAccount

        registry.add_account(account)

        search_result = registry.search_account(pesel)

        if should_find:
            assert search_result == account
        else:
            assert search_result is False

    def test_return_accounts(self, registry, personalAccount):
        registry.add_account(personalAccount)

        result = registry.return_accounts()

        assert result == registry.accounts

    def test_return_number_of_accounts(self, registry, personalAccount):
        registry.add_account(personalAccount)

        result = registry.return_number_of_accounts()

        assert result == len(registry.accounts)




