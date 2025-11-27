from flask import Flask, request, jsonify
from src.personalaccount import AccountRegistry
from src.personalaccount import PersonalAccount
app = Flask(__name__)
registry = AccountRegistry()
@app.route("/api/accounts", methods=['POST'])
def create_account():
    data = request.get_json()
    print(f"Create account request: {data}")
    personalAccount = PersonalAccount(data["name"],data["surname"],data["pesel"])
    registry.add_account(account=personalAccount)
    return jsonify({"message": "Account created"}), 201

@app.route("/api/accounts", methods=['GET'])
def get_all_accounts():
    print("Get all accounts request received")
    accounts = registry.return_accounts()
    accounts_data = [{"name": acc.first_name, "surname": acc.last_name, "pesel": acc.pesel, "balance": acc.balance} for acc in accounts]
    return jsonify(accounts_data), 200
@app.route("/api/accounts/count", methods=['GET'])
def get_account_count():
    print("Get account count request received")
    count = registry.return_number_of_accounts()
    return jsonify({"count": count}), 200
@app.route("/api/accounts/<pesel>", methods=['GET'])
def get_account_by_pesel(pesel):
    account = registry.search_account(pesel)
    if account:
        return jsonify({"name": account.first_name, "surname": account.last_name,"pesel": account.pesel}), 200
    return jsonify({"message": "Account not found"}), 404

@app.route("/api/accounts/<pesel>", methods=['PATCH'])
def update_account(pesel):
    data = request.get_json()
    account : PersonalAccount = registry.search_account(pesel)
    if not account : return jsonify({"message": "Account not found"}), 404
    if data["name"] : account.first_name = data["name"]
    if data["surname"] : account.last_name = data["surname"]
    return jsonify({"message": "Account updated"}), 200
@app.route("/api/accounts/<pesel>", methods=['DELETE'])
def delete_account(pesel):
    account: PersonalAccount = registry.search_account(pesel)

    registry.accounts.remove(account)
    return jsonify({"message": "Account deleted"}), 200

