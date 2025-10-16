from src.account import Account


class TestAccount:
    def test_account_creation(self):
        account = Account("John", "Doe",'13432134654')
        assert account.first_name == "John"
        assert account.last_name == "Doe"
        assert account.balance == 0.0
        assert account.pesel == '13432134654'
        assert len(account.pesel) == 11