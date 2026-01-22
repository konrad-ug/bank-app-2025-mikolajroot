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
