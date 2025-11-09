from threading import active_count

from src.personalaccount import PersonalAccount, Account
from src.personalaccount import CompanyAccount

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
        assert account.history == [-51,-5.0]