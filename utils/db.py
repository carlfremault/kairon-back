import sqlite3


def get_db_connection():
    conn = sqlite3.connect("kairon.db")
    conn.row_factory = sqlite3.Row
    return conn


def fetch_data(query, params=None):
    db = get_db_connection()
    if params:
        cursor = db.execute(query, params)
    else:
        cursor = db.execute(query)
    data = [dict(row) for row in cursor.fetchall()]
    db.close()
    return data


def execute_query(query, params=None):
    db = get_db_connection()
    db.execute(query, params)
    db.commit()
    db.close()
