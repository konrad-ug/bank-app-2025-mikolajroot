import pytest
from app.api import app as flask_app, registry
import json

class TestCrud:
    @pytest.fixture()
    def client(self):
        flask_app.config['TESTING'] = True

        registry.accounts = []

        with flask_app.test_client() as client:
            yield client

    @pytest.fixture
    def sample_account_payload(self):
        return {
            "name": "Adam",
            "surname": "Nowak",
            "pesel": "90010112345"
        }

    @pytest.fixture
    def create_account(self,client, sample_account_payload):
        client.post("/api/accounts", json=sample_account_payload)
        return sample_account_payload

    def test_create_account_with_existing_pesel(self,client,sample_account_payload):
        client.post("/api/accounts", json=sample_account_payload)
        response = client.post("/api/accounts", json=sample_account_payload)

        assert response.status_code == 409


    @pytest.mark.parametrize("test_data", [
        {"name": "Jan", "surname": "Kowalski", "pesel": "12345678901"},
        {"name": "Anna", "surname": "Ziemniak", "pesel": "98765432109"}
    ])
    def test_get_account_by_pesel(self,client, test_data):
        client.post("/api/accounts", json=test_data)

        response = client.get(f"/api/accounts/{test_data['pesel']}")

        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == test_data["name"]
        assert data["pesel"] == test_data["pesel"]

    def test_get_account_not_found(self,client):
        non_existent_pesel = "00000000000"
        response = client.get(f"/api/accounts/{non_existent_pesel}")

        assert response.status_code == 404

    def test_update_account(self,client, create_account):
        pesel = create_account["pesel"]
        update_data = {
            "name": "Adam Updated",
            "surname": "Nowak Updated"
        }

        response = client.patch(f"/api/accounts/{pesel}", json=update_data)
        assert response.status_code == 200

        get_response = client.get(f"/api/accounts/{pesel}")
        updated_account = get_response.get_json()
        assert updated_account["name"] == "Adam Updated"
        assert updated_account["surname"] == "Nowak Updated"

    def test_delete_account(self,client, create_account):
        pesel = create_account["pesel"]

        response = client.delete(f"/api/accounts/{pesel}")
        assert response.status_code == 200
        assert response.get_json()["message"] == "Account deleted"

        get_response = client.get(f"/api/accounts/{pesel}")
        assert get_response.status_code == 404

    def test_transfer_account_doesnt_exists(self,client,create_account):
        non_existent_pesel = "00000000000"
        request_body = {
            "amount": 100,
            "type": "incoming"
        }
        response = client.post(f"/api/accounts/{non_existent_pesel}/transfer", json=request_body)

        assert  response.status_code == 404

    def test_incoming_transfer(self,client,create_account):
        pesel = create_account["pesel"]
        request_body = {
            "amount": 100,
            "type": "incoming"
        }

        response = client.post(f"/api/accounts/{pesel}/transfer", json=request_body)

        assert response.status_code == 200

    def test_outgoing_success_transfer(self,client,create_account):
        pesel = create_account["pesel"]
        request_body1 = {
            "amount": 2,
            "type": "outgoing"
        }
        request_body2 = {
            "amount": 100,
            "type": "incoming"
        }

        client.post(f"/api/accounts/{pesel}/transfer", json=request_body2)

        response = client.post(f"/api/accounts/{pesel}/transfer", json=request_body1)

        assert response.status_code == 200

    def test_outgoing_failure_transfer(self,client,create_account):
        pesel = create_account["pesel"]
        request_body = {
            "amount": 1000,
            "type": "outgoing"
        }
        response = client.post(f"/api/accounts/{pesel}/transfer", json=request_body)

        assert response.status_code == 422

    def test_express_failure_transfer(self, client, create_account):
        pesel = create_account["pesel"]
        request_body = {
            "amount": 1000,
            "type": "express"
        }
        response = client.post(f"/api/accounts/{pesel}/transfer", json=request_body)

        assert response.status_code == 422

    def test_express_success_transfer(self, client, create_account):
        pesel = create_account["pesel"]
        request_body1 = {
            "amount": 2,
            "type": "express"
        }
        request_body2 = {
            "amount": 100,
            "type": "incoming"
        }

        client.post(f"/api/accounts/{pesel}/transfer", json=request_body2)

        response = client.post(f"/api/accounts/{pesel}/transfer", json=request_body1)

        assert response.status_code == 200

    def test_wrong_type(self,client,create_account):
        pesel = create_account['pesel']

        request_body = {
            "amount": 100,
            "type": "sghjbhjfgbsdahjbfgj"
        }

        response = client.post(f"/api/accounts/{pesel}/transfer", json=request_body)

        assert response.status_code == 400

    def test_save_accounts_success(self, client, create_account, monkeypatch):
        class DummyRepo:
            def __init__(self):
                pass

            def save_all(self, reg):
                return len(reg.return_accounts())

            def close(self):
                pass

        monkeypatch.setattr("app.api.MongoAccountsRepository", DummyRepo)

        response = client.post("/api/accounts/save")

        assert response.status_code == 200
        assert response.get_json()["message"] == "Saved 1 accounts to database"

    def test_save_accounts_failure(self, client, monkeypatch):
        class FailingRepo:
            def __init__(self, *args, **kwargs):
                pass

            def save_all(self, reg):
                raise RuntimeError("db down")

            def close(self):
                pass

        monkeypatch.setattr("app.api.MongoAccountsRepository", FailingRepo)

        response = client.post("/api/accounts/save")

        assert response.status_code == 500
        assert "Error saving accounts" in response.get_json()["message"]