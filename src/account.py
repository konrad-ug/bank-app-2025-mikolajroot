import os

import requests
from datetime import date, datetime
from lib.smtp import SMTPClient
from pymongo import MongoClient

class Account:

    fee_for_express_transfer = 1.0

    def __init__(self):
        self.balance = 0.0
        self.history = []

    def transfer_in(self,money: float) -> None:
        if money > 0:
            self.balance += money
            self.history.append(money)

    def transfer_out(self,money: float):
        if 0 < money <= self.balance:
            self.balance -= money
            self.history.append(-money)

    def express_transfer_out(self,money):
        if 0 < money <= self.balance + self.fee_for_express_transfer:
            self.balance -= money + self.fee_for_express_transfer
            self.history.append(-money)
            self.history.append(-self.fee_for_express_transfer)

    def send_history_via_email(self,email_Address):
        dateNow = datetime.now()
        subject = f"Account Transfer History {dateNow.strftime('%Y-%m-%d')}"
        text = ""
        if self.__class__.__name__ == "PersonalAccount":
            text = f'Personal account history: {self.history}'
        elif self.__class__.__name__ == "CompanyAccount":
            text = f'Company account history: {self.history}'

        client = SMTPClient() 

        result = client.send(subject,text,email_Address)
        return result





#personal
class PersonalAccount(Account):

    fee_for_express_transfer = 1.0

    def __init__(self, first_name, last_name, pesel, promoCode=None):
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.pesel = pesel if self.is_pesel_valid(pesel) else 'Invalid'
        self.balance = 50.0 if self.is_promoCode_valid(promoCode) and self.is_person_age_good(pesel) else 0
        self.history = []


    def is_pesel_valid(self,pesel):
        if isinstance(pesel,str) and len(pesel) == 11:
            return True

    def is_promoCode_valid(self,promoCode):
        if promoCode is not None and promoCode.startswith('PROM_') and len(promoCode) == 8:
            return True
    def is_person_age_good(self,pesel):
        if pesel != "Invalid":
            if  25 > int(pesel[0:2]) or int(pesel[0:2]) > 60 :
                return True

    def last_three_tranfer_in(self):
        if len(self.history) >= 3:
            if all(i > 0 for i in self.history[-3:]):
                return True
            else: return False
        else:
            return False


    def submit_for_loan(self,amount):
        if self.last_three_tranfer_in() or (len(self.history) >= 5 and sum(self.history[-5:]) > amount):
            self.balance += amount
            return True
        else:
            return False


#company
class CompanyAccount(Account): # pragma: no cover

    fee_for_express_transfer = 5.0

    def __init__(self, company_name, nip):
        super().__init__()
        self.company_name = company_name
        self.nip = nip if self.is_nip_valid(nip) else 'Invalid'
        self.history = []

        if self.is_nip_valid(nip):
            self.nip = nip
            if not self.check_vat_status(nip):
                raise ValueError("Company not registered!!")
        else:
            self.nip = "Invalid"
    def is_nip_valid(self,nip):
        if isinstance(nip,str) and len(nip) == 10:
            return True
        return False

    def balance_two_times_amount(self,amount):
        if self.balance > 2*amount:
            return True
        return False

    def is_zus_payed(self):
        if -1775 in self.history:
            return True
        return False

    def submit_for_loan(self,amount):
        if self.balance_two_times_amount(amount) and self.is_zus_payed():
            self.balance += amount
            return True
        return False

    def check_vat_status(self,nip):
        today = date.today()
        formatted_date = today.strftime("%Y-%m-%d")

        os.environ["BANK_APP_MF_URL"] = f"https://wl-api.mf.gov.pl/api/search/nip/{nip}?date={formatted_date}"

        response = requests.get(os.environ['BANK_APP_MF_URL'])

        data = response.json()

        if data['result']['subject']['statusVat'] == "Czynny":
            print("Vat jest czynny")
            return True


        return False

class AccountRegistry:
    def __init__(self):
        self.accounts = []

    def add_account(self, account: PersonalAccount):
        self.accounts.append(account)

    def search_account(self,pesel):
        for account in self.accounts:
            if account.pesel == pesel:
                return account
        return False

    def return_accounts(self):
        return self.accounts

    def return_number_of_accounts(self):
        return len(self.accounts)

class MongoAccountsRepository:
    def __init__(self, connection_string="mongodb://localhost:27017/", database_name="bank_app"):

        self.client = MongoClient(connection_string)
        self.db = self.client[database_name]
        self.collection = self.db["accounts"]

    def save_all(self, registry: AccountRegistry):
        self.collection.delete_many({})
        
        accounts_data = []
        for account in registry.return_accounts():
            if isinstance(account, PersonalAccount):
                account_dict = {
                    "first_name": account.first_name,
                    "last_name": account.last_name,
                    "pesel": account.pesel,
                    "balance": account.balance,
                    "history": account.history
                }
                accounts_data.append(account_dict)
        
        if accounts_data:
            self.collection.insert_many(accounts_data)
        
        return len(accounts_data)

    def close(self):
        self.client.close()
