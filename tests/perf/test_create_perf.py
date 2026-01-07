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
        response_create = requests.post(url_post, json=payload)
        
        try:
            response_create = requests.post(url_post, json=payload, timeout=timeout_limit)

            assert response_create.status_code == 201, \
                f"Błąd tworzenia konta w iteracji {i}. Status: {response_create.status_code}"

        except Timeout:
            pytest.fail(f"Tworzenie konta w iteracji {i} przekroczyło limit czasu {timeout_limit}s!")
        
        try:
            response_delete = requests.delete(url_delete, timeout=timeout_limit)
            
            assert response_delete.status_code == 200, \
                f"Błąd usuwania konta w iteracji {i}. Status: {response_delete.status_code}"

        except Timeout:
            pytest.fail(f"Usuwanie konta w iteracji {i} przekroczyło limit czasu {timeout_limit}s!")



        url_delete = f"{BASE_URL}/api/accounts/{pesel}"
        
        try:
            response_delete = requests.delete(url_delete, timeout=timeout_limit)
            
            assert response_delete.status_code == 200, \
                f"Błąd usuwania konta w iteracji {i}. Status: {response_delete.status_code}"

        except Timeout:
            pytest.fail(f"Usuwanie konta w iteracji {i} przekroczyło limit czasu {timeout_limit}s!")