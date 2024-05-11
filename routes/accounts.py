from flask import jsonify, request
from utils.db import *
from utils.exchanges import *


def get_accounts():
    try:
        accounts = fetch_data("SELECT id, account_name, exchange_name FROM accounts")
        return jsonify(accounts)
    except Exception as e:
        error_message = f"Error fetching accounts: {e}"
        return jsonify({"error": error_message}), 500


def add_account():
    new_account = request.get_json()
    account_name = new_account["account_name"]
    exchange_name = new_account["exchange_name"]
    public_key = new_account["public_key"]
    private_key = new_account["private_key"]

    if verify_exchange_credentials(exchange_name, public_key, private_key) is True:
        try:
            execute_query(
                "INSERT INTO accounts (account_name, exchange_name, public_key, private_key) VALUES (?, ?, ? , ?)",
                (account_name, exchange_name, public_key, private_key),
            )
            return jsonify(""), 204
        except Exception as e:
            error_message = f"Error adding account: {e}"
            return jsonify({"error": error_message}), 500

    else:
        return jsonify("Invalid credentials"), 400
