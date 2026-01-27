import pytest

from src.account import MongoAccountsRepository, AccountRegistry, PersonalAccount


@pytest.fixture()
def mock_mongo(mocker):
    mock_collection = mocker.MagicMock()
    mock_client = mocker.MagicMock()
    mock_client.__getitem__.return_value = {"accounts": mock_collection}
    mocker.patch("src.account.MongoClient", return_value=mock_client)
    return mock_client, mock_collection


def test_save_all_persists_accounts(mock_mongo):
    mock_client, mock_collection = mock_mongo

    registry = AccountRegistry()
    registry.add_account(PersonalAccount("Jan", "Kowalski", "12345678901"))

    repo = MongoAccountsRepository(connection_string="mongodb://test", database_name="bank_app")
    saved = repo.save_all(registry)

    mock_collection.delete_many.assert_called_once_with({})
    mock_collection.insert_many.assert_called_once()
    inserted_payload = mock_collection.insert_many.call_args[0][0]
    assert inserted_payload[0]["pesel"] == "12345678901"
    assert saved == 1

    repo.close()
    mock_client.close.assert_called_once()


def test_save_all_skips_empty_registry(mock_mongo):
    mock_client, mock_collection = mock_mongo

    registry = AccountRegistry()

    repo = MongoAccountsRepository(connection_string="mongodb://test", database_name="bank_app")
    saved = repo.save_all(registry)

    mock_collection.delete_many.assert_called_once_with({})
    mock_collection.insert_many.assert_not_called()
    assert saved == 0

    repo.close()
    mock_client.close.assert_called_once()


def test_load_all_clears_and_loads_accounts(mock_mongo):
    mock_client, mock_collection = mock_mongo

    mock_refs = [
        {
            "first_name": "Jan",
            "last_name": "Kowalski",
            "pesel": "12345678901",
            "balance": 150.0,
            "history": [100.0, 50.0]
        },
        {
            "first_name": "Anna",
            "last_name": "Nowak",
            "pesel": "98765432109",
            "balance": 75.5,
            "history": [100.0, -24.5]
        }
    ]
    mock_collection.find.return_value = mock_refs


    registry = AccountRegistry()
    registry.add_account(PersonalAccount("Old", "Account", "11111111111"))
    assert len(registry.return_accounts()) == 1

    repo = MongoAccountsRepository(connection_string="mongodb://test", database_name="bank_app")
    loaded = repo.load_all(registry)

    # Verify registry was cleared and repopulated
    assert loaded == 2
    assert len(registry.return_accounts()) == 2

    # Verify account data
    jan = registry.search_account("12345678901")
    assert jan is not False
    assert jan.first_name == "Jan"
    assert jan.last_name == "Kowalski"
    assert jan.balance == 150.0
    assert jan.history == [100.0, 50.0]

    anna = registry.search_account("98765432109")
    assert anna is not False
    assert anna.first_name == "Anna"
    assert anna.last_name == "Nowak"
    assert anna.balance == 75.5
    assert anna.history == [100.0, -24.5]

    repo.close()
    mock_client.close.assert_called_once()


def test_load_all_clears_registry_before_loading(mock_mongo):
    mock_client, mock_collection = mock_mongo

    # Mock empty database
    mock_collection.find.return_value = []

    # Create registry with existing accounts
    registry = AccountRegistry()
    registry.add_account(PersonalAccount("Old", "Account", "11111111111"))
    assert len(registry.return_accounts()) == 1

    # Load from empty database
    repo = MongoAccountsRepository(connection_string="mongodb://test", database_name="bank_app")
    loaded = repo.load_all(registry)

    # Verify registry was cleared
    assert loaded == 0
    assert len(registry.return_accounts()) == 0

    repo.close()
    mock_client.close.assert_called_once()
