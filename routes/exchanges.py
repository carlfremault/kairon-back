from flask import jsonify
import ccxt


def get_exchanges():
    try:
        return jsonify(ccxt.exchanges)
    except Exception as e:
        error_message = f"Error fetching exchanges: {e}"
        return jsonify({"error": error_message}), 500
