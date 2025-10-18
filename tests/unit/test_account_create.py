from src.account import Account


class TestAccount:
    def test_account_creation(self):
        account = Account("John", "Doe",'134321346542')
        assert account.first_name == "John"
        assert account.last_name == "Doe"
        assert account.balance == 0.0
        assert account.pesel == 'Invalid'

    def test_pesel_too_long(self):
        account = Account("Jane","Doe",'4234324342424234')
        assert account.pesel == 'Invalid'

    def test_pesel_too_short(self):
        account = Account("Jane","Doe",'871368')
        assert account.pesel == 'Invalid'

    def test_pesel_empty(self):
        account = Account("Jane", "Doe", '')
        assert account.pesel == 'Invalid'

    def test_correct_promoCode(self):
        account = Account("Jane", "Doe", '','PROM_123')
        assert account.balance == 50.0

    def test_too_long_promoCode(self):
        account = Account("Jane", "Doe", '','PROM_1234')
        assert account.balance == 0.0

    def test_too_short_promoCode(self):
        account = Account("Jane", "Doe", '','PROM_12')
        assert account.balance == 0.0

    def test_bad_promoCode(self):
        account = Account("Jane", "Doe", '','PROM-123')
        assert account.balance == 0.0

    def test_to_old(self):
        account = Account("Jane", "Doe", '55232465786', 'PROM_123')
        assert account.balance == 0.0

    def test_young(self):
        account = Account("Jane", "Doe", '62232465786', 'PROM-123')
        assert account.balance == 50.0

