from flask import Flask, request, jsonify
from src.account import AccountRegistry
from src.account import PersonalAccount
from src.account import MongoAccountsRepository
app = Flask(__name__)
registry = AccountRegistry()
@app.route("/api/accounts", methods=['POST'])
def create_account():
    data = request.get_json()
    print(f"Create account request: {data}")
    if registry.search_account(data["pesel"]) :
        return jsonify({"message": "Account with this pesel exists"}), 409
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
        return jsonify({"name": account.first_name, "surname": account.last_name,"pesel": account.pesel,"balance":account.balance}), 200
    return jsonify({"message": "Account not found"}), 404

@app.route("/api/accounts/<pesel>", methods=['PATCH'])
def update_account(pesel):
    data = request.get_json()
    account : PersonalAccount | bool = registry.search_account(pesel)
    if not account : return jsonify({"message": "Account not found"}), 404
    if data["name"] : account.first_name = data["name"]
    if data["surname"] : account.last_name = data["surname"]
    return jsonify({"message": "Account updated"}), 200

@app.route("/api/accounts/<pesel>", methods=['DELETE'])
def delete_account(pesel):
    account: PersonalAccount = registry.search_account(pesel)

    registry.accounts.remove(account)
    return jsonify({"message": "Account deleted"}), 200

@app.route("/api/accounts/<pesel>/transfer", methods=['POST'])
def transfer(pesel):
    data = request.get_json()
    account : PersonalAccount | bool = registry.search_account(pesel)
    if not account : return jsonify({"message": "Account not found"}), 404

    match data['type']:
        case "incoming":
            account.transfer_in(data['amount'])
            return jsonify({"message": "The order has been accepted for processing"}), 200
        case "outgoing":
            balance = account.balance
            account.transfer_out(data['amount'])
            if account.balance == balance - data['amount']: return jsonify({"message": "The order has been accepted for processing"}), 200
            return jsonify({"message": "Transaction failed"}), 422
        case "express":
            balance = account.balance
            account.express_transfer_out(data['amount'])
            if account.balance == balance - data['amount'] - account.fee_for_express_transfer: return  jsonify({"message": "The order has been accepted for processing"}), 200
            return jsonify({"message": "Transaction failed"}), 422
        case _:
            return jsonify({"message": "Type doesn`t exits"}), 400

@app.route("/api/accounts/save", methods=['POST'])
def save_accounts():
    try:
        repo = MongoAccountsRepository()
        saved_count = repo.save_all(registry)
        repo.close()
        return jsonify({"message": f"Saved {saved_count} accounts to database"}), 200
    except Exception as e:
        return jsonify({"message": f"Error saving accounts: {str(e)}"}), 500

@app.route("/api/accounts/load", methods=['POST'])
def load_accounts():
    try:
        repo = MongoAccountsRepository()
        loaded_count = repo.load_all(registry)
        repo.close()
        return jsonify({"message": f"Loaded {loaded_count} accounts from database"}), 200
    except Exception as e:
        return jsonify({"message": f"Error loading accounts: {str(e)}"}), 500
