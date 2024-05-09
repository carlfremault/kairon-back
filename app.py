from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect("kairon.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/accounts")
def get_accounts():
    db = get_db_connection()
    cursor = db.execute("SELECT * FROM accounts")
    accounts = [dict(row) for row in cursor.fetchall()]
    db.close()
    return jsonify(accounts)


@app.route("/accounts", methods=["POST"])
def add_account():
    new_account = request.get_json()

    account_name = new_account["name"]
    exchange_name = new_account["exchange"]
    public_key = new_account["public_key"]
    private_key = new_account["private_key"]

    db = get_db_connection()
    db.execute(
        "INSERT INTO accounts (account_name, exchange_name, public_key, private_key) VALUES (?, ?, ? , ?)",
        (account_name, exchange_name, public_key, private_key),
    )
    db.commit()
    db.close()
    return "", 204
