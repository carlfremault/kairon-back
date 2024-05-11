from .db import *


def get_account_info(id):
    db = get_db_connection()
    cursor = db.execute(
        "SELECT exchange_name, public_key, private_key FROM accounts WHERE id = ?", (id)
    )
    info = [dict(row) for row in cursor.fetchall()]
    db.close()
    return info
