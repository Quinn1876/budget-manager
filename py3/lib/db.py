from typing import Any, TypedDict
from psycopg2.extensions import cursor as Cursor
import os
import psycopg2
from contextlib import contextmanager

__CHECK_CSV__ = """
SELECT COUNT(*) FROM csv_history WHERE path = %(path)s
"""
__INSERT_CSV__ = """
INSERT INTO csv_history (id, path) VALUES (uuid_generate_v4(), %(path)s);
"""

__SELECT_ACCOUNT_NUMBERS__ = """
SELECT DISTINCT account_number FROM account
"""

__INSERT_ACCOUNT__ = """
INSERT INTO account (account_number, account_type) VALUES (%(account_number)s, %(account_type)s);
"""

__INSERT_TRANSACTION__ = """
INSERT INTO transactions (transaction_id, account_number, date, description_1, description_2, amount, currency) VALUES (uuid_generate_v4(), %(account_number)s, %(date)s, %(description1)s, %(description2)s, %(amount)s, %(currency)s);
"""

class InsertAccount(TypedDict):
    account_number: str
    account_type: str

class InsertTransaction(TypedDict):
    account_number: str
    date: str
    description1: str
    description2: str
    amount: str
    currency: str

@contextmanager
def get_cursor():
    dbname=os.getenv("POSTGRES_DB")
    user=os.getenv("POSTGRES_USER")
    password=os.getenv("POSTGRES_PASSWORD")
    print(f"dbname: {dbname}")
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host="database",
        port="5432"
    )
    try:
        yield conn.cursor()
    finally:
        conn.close()

def build_set_clause(fields: list[str], request: dict[str, Any]):
    fields_to_update = []
    values = []
    # Dynamically build SET clauses
    for field in fields:
        if field in request:
            fields_to_update.append(f"{field} = %s")
            values.append(request[field])
    return fields_to_update, values

def get_csv_count(cursor: Cursor, path: str) -> int:
    cursor.execute(__CHECK_CSV__, { "path": path })
    result = cursor.fetchone()
    if result is None: return 0
    return result[0]

def insert_csv(cursor: Cursor, path: str):
    cursor.execute(__INSERT_CSV__, { "path": path })

def get_all_account_numbers(cursor: Cursor) -> set[str]:
    cursor.execute(__SELECT_ACCOUNT_NUMBERS__)
    return set(map(lambda row: row[0], cursor.fetchall()))

def insert_account(cursor: Cursor, account: InsertAccount):
    cursor.execute(__INSERT_ACCOUNT__, account)

def insert_transaction(cursor: Cursor, transaction: InsertTransaction):
    cursor.execute(__INSERT_TRANSACTION__, transaction)
