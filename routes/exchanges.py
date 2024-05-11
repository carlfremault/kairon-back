from flask import jsonify
import ccxt


def get_exchanges():
    return jsonify(ccxt.exchanges)
