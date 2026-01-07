import random
import pytest
import requests
from requests import Timeout
from faker import Faker

import pytest
import requests

BASE_URL = "http://localhost:5000"
fake = Faker()

def test_performance_create_and_delete_100_accounts():

    timeout_limit = 0.5
    
    for i in range(100):
        pesel = ''.join([str(random.randint(0, 9)) for _ in range(11)])
        
        
        payload = {
            "name": fake.first_name(),
            "surname": fake.last_name(),
            "pesel": pesel
        }


        url_post = f"{BASE_URL}/api/accounts"

        try:
            response_create = requests.post(url_post, json=payload, timeout=timeout_limit)

            assert response_create.status_code == 201, \
                f"Error creating account in iteration {i}. Status: {response_create.status_code}"

        except Timeout:
            pytest.fail(f"Creating account {i} exceeded limit {timeout_limit}s!")


        url_delete = f"{BASE_URL}/api/accounts/{pesel}"
        
        try:
            response_delete = requests.delete(url_delete, timeout=timeout_limit)
            
            assert response_delete.status_code == 200, \
                f"Error deleting account in iteration {i}. Status: {response_delete.status_code}"

        except Timeout:
            pytest.fail(f"Deleting account {i} excedeed limit {timeout_limit}s!")



def test_performance_create_and_make_100_incoming_transfers():

    timeout_limit = 0.5

    pesel = ''.join([str(random.randint(0, 9)) for _ in range(11)])
        
        
    payload = {
            "name": fake.first_name(),
            "surname": fake.last_name(),
            "pesel": pesel
        }
    
    url_post = f"{BASE_URL}/api/accounts"


    try:
        response_create = requests.post(url_post, json=payload, timeout=timeout_limit)

        assert response_create.status_code == 201, \
            f"Error creating account. Status: {response_create.status_code}"

    except Timeout:
        pytest.fail(f"Deleting account excedeed limit {timeout_limit}s!")


    sumOfTransfers = 0
    
    for i in range(100):

        url_incoming_transfer = f'{BASE_URL}/api/accounts/{pesel}/transfer'

        amount= random.randint(1,1000)

        sumOfTransfers += amount

        payload = {
            "type": "incoming",
            "amount": amount
        }

        try:
            response_tranfer = requests.post(url_incoming_transfer, json=payload, timeout=timeout_limit)

            assert response_tranfer.status_code == 200, \
            f"Error transfer {i}. Status: {response_tranfer.status_code}"

        except Timeout:
            pytest.fail(f"Transfer {i} excedeed limit {timeout_limit}s!")
        
    try:
        response_get = requests.get(f"{BASE_URL}/api/accounts/{pesel}", timeout=timeout_limit)
        assert response_get.status_code == 200
        
        account_data = response_get.json()
        actual_balance = account_data["balance"]
        
        assert abs(actual_balance - sumOfTransfers) < 0.01, \
            f"Balance mismatch Expected: {sumOfTransfers}, Actual: {actual_balance}"
        
        print(f" Balance verified: {actual_balance} (100 transfers completed)")
        
    except Timeout:
        pytest.fail("Getting account balance exceeded timeout")