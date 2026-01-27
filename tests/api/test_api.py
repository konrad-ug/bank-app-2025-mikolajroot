import pytest
from app.api import app as flask_app, registry
from src.account import PersonalAccount, MongoAccountsRepository
import json
from pymongo import MongoClient

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

    def test_save_accounts_success(self, client, create_account):
        response = client.post("/api/accounts/save")

        assert response.status_code == 200
        assert "Saved 1 accounts to database" in response.get_json()["message"]
        
        
        mongo_repo = MongoAccountsRepository()
        saved_refs = list(mongo_repo.collection.find({}))
        mongo_repo.close()
        
        assert len(saved_refs) == 1
        assert saved_refs[0]["pesel"] == "90010112345"

    def test_save_accounts_empty_registry(self, client):
        response = client.post("/api/accounts/save")

        assert response.status_code == 200
        assert "Saved 0 accounts to database" in response.get_json()["message"]
        
        mongo_repo = MongoAccountsRepository()
        saved_refs = list(mongo_repo.collection.find({}))
        mongo_repo.close()
        
        assert len(saved_refs) == 0

    def test_load_accounts_success(self, client, create_account):
        client.post("/api/accounts/save")
        
        registry.accounts.clear()
        assert len(registry.return_accounts()) == 0
        
        response = client.post("/api/accounts/load")

        assert response.status_code == 200
        assert "Loaded 1 accounts from database" in response.get_json()["message"]
        
        assert len(registry.return_accounts()) == 1
        loaded_account = registry.return_accounts()[0]
        assert loaded_account.first_name == "Adam"
        assert loaded_account.last_name == "Nowak"
        assert loaded_account.pesel == "90010112345"

    def test_load_accounts_clears_registry(self, client, create_account):
        client.post("/api/accounts/save")
        
        registry.add_account(PersonalAccount("Extra", "Account", "22222222222"))
        assert len(registry.return_accounts()) == 2
        
        response = client.post("/api/accounts/load")

        assert response.status_code == 200
        assert len(registry.return_accounts()) == 1
        assert registry.return_accounts()[0].pesel == "90010112345"