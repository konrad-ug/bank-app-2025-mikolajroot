from datetime import datetime


class Account:

    fee_for_express_transfer = 1.0

    def __init__(self):
        self.balance = 0.0
        self.history = []

    def transfer_in(self,money: float) -> None:
        if money > 0:
            self.balance += money
            self.history.append(money)

    def transfer_out(self,money: float) -> None:
        if 0 < money <= self.balance:
            self.balance -= money
            self.history.append(-money)

    def express_transfer_out(self,money):
        if 0 < money <= self.balance + self.fee_for_express_transfer:
            self.balance -= money + self.fee_for_express_transfer
            self.history.append(-money)
            self.history.append(-self.fee_for_express_transfer)



#personal
class PersonalAccount(Account):

    fee_for_express_transfer = 1.0

    def __init__(self, first_name, last_name,pesel,promoCode=None):
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
class CompanyAccount(Account):

    fee_for_express_transfer = 5.0

    def __init__(self, company_name,nip):
        self.company_name = company_name
        self.nip = nip if self.is_nip_valid(nip) else 'Invalid'
        self.history = []
    def is_nip_valid(self,pesel):
        if isinstance(pesel,str) and len(pesel) == 10:
            return True

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

class AccountRegistry:
    def __init__(self):
        self.accounts = []

    def add_account(self, account: PersonalAccount):
        self.accounts.append(account)