from flask import jsonify, request
from utils.db import *
from utils.exchanges import *


def get_accounts():
    db = get_db_connection()
    cursor = db.execute("SELECT id, account_name, exchange_name FROM accounts")
    accounts = [dict(row) for row in cursor.fetchall()]
    db.close()
    return jsonify(accounts)


def add_account():
    new_account = request.get_json()
    account_name = new_account["account_name"]
    exchange_name = new_account["exchange_name"]
    public_key = new_account["public_key"]
    private_key = new_account["private_key"]

    if verify_exchange_credentials(exchange_name, public_key, private_key) is True:
        db = get_db_connection()
        db.execute(
            "INSERT INTO accounts (account_name, exchange_name, public_key, private_key) VALUES (?, ?, ? , ?)",
            (account_name, exchange_name, public_key, private_key),
        )
        db.commit()
        db.close()
        response = jsonify("")
        return response, 204
    else:
        return jsonify("Invalid credentials"), 400
