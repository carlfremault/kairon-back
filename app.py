from flask import Flask, jsonify, request
from flask_cors import CORS
from routes import exchanges, accounts, markets

app = Flask(__name__)
CORS(app, resources=r"/api/*")


def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response


@app.after_request
def after_request(response):
    return add_cors_headers(response)


# ACCOUNTS
app.route("/api/accounts")(accounts.get_accounts)
app.route("/api/accounts", methods=["POST"])(accounts.add_account)

# EXCHANGES
app.route("/api/exchanges")(exchanges.get_exchanges)


# MARKETS
app.route("/api/markets/<id>/all")(markets.get_all_exchange_markets)
app.route("/api/markets")(markets.get_markets)
app.route("/api/markets", methods=["POST"])(markets.add_market)
