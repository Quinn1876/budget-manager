import uuid
from ariadne import QueryType, MutationType, ObjectType
from py3.lib import db
from py3.lib.db import get_cursor

query = QueryType()
mutation = MutationType()
account_obj = ObjectType("Account")
transaction_obj = ObjectType("Transaction")

@query.field("listAccounts")
def resolve_accounts(*_):
    with get_cursor() as cur:
        cur.execute("SELECT account_number, account_type, owner, account_name FROM account")
        return [
            {
                "account_number": row[0],
                "account_type": row[1],
                "owner": row[2],
                "account_name": row[3],
            }
            for row in cur.fetchall()
        ]

@query.field("getAccount")
def resolve_account(_, info, account_number):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM account WHERE account_number = %s", (account_number,))
        row = cur.fetchone()
        if row:
            return {
                "account_number": row[0],
                "account_type": row[1],
                "owner": row[2],
                "account_name": row[3],
                "initial_balance": row[4]
            }

@query.field("listTransactions")
def resolve_transactions(_, info, account_number=None):
    with get_cursor() as cur:
        if account_number:
            cur.execute("SELECT * FROM transactions WHERE account_number = %s", (account_number,))
        else:
            cur.execute("SELECT * FROM transactions")
        return [
            {
                "account_number": row[0],
                "date": str(row[1]),
                "description_1": row[2],
                "description_2": row[3],
                "amount": float(row[4]),
                "currency": row[5].strip(),
                "transaction_id": str(row[6])
            }
            for row in cur.fetchall()
        ]

@query.field("getTransaction")
def resolve_transaction(_, info, transaction_id):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM transactions WHERE transaction_id = %s", (transaction_id,))
        row = cur.fetchone()
        if row:
            return {
                "account_number": row[0],
                "date": str(row[1]),
                "description_1": row[2],
                "description_2": row[3],
                "amount": float(row[4]),
                "currency": row[5].strip(),
                "transaction_id": str(row[6])
            }

@transaction_obj.field("account")
def resolve_transaction_account(obj, *_):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM account WHERE account_number = %s", (obj["account_number"],))
        row = cur.fetchone()
        if row:
            return {
                "account_number": row[0],
                "account_type": row[1],
                "owner": row[2],
                "account_name": row[3],
                "initial_balance": row[4]
            }

@account_obj.field("transactions")
def resolve_account_transactions(obj, *_):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM transactions WHERE account_number = %s", (obj["account_number"],))
        return [
            {
                "account_number": row[0],
                "date": str(row[1]),
                "description_1": row[2],
                "description_2": row[3],
                "amount": row[4],
                "currency": row[5].strip(),
                "transaction_id": str(row[6])
            }
            for row in cur.fetchall()
        ]

@account_obj.field("balance")
def resolve_account_balance(obj, *_):
    with get_cursor() as cur:
        cur.execute("SELECT sum(t.amount) as balance FROM transactions as t where t.account_number = %s", (obj["account_number"],))
        row = cur.fetchone()
        if row:
            return row[0] + obj["initial_balance"]

@mutation.field("createTransaction")
def resolve_create_transaction(_, info, input):
    transaction_id = str(uuid.uuid4())
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO transactions (transaction_id, account_number, date, description_1, description_2, amount, currency)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            transaction_id,
            input["account_number"],
            input["date"],
            input.get("description_1"),
            input.get("description_2"),
            input["amount"],
            input.get("currency", "CAD$")
        ))
        cur.connection.commit()
    input["transaction_id"] = transaction_id
    return input

@mutation.field("createAccount")
def resolve_create_account(_, info, input):
    with get_cursor() as cur:
        cur.execute("""
            INSERT INTO account (account_number, account_type, owner, account_name)
            VALUES (%s, %s, %s, %s)
        """, (
            input["account_number"],
            input["account_type"],
            input.get("owner", "Quinn"),
            input.get("account_name", "")
        ))
        cur.connection.commit()
    return input

@mutation.field("updateAccount")
def resolve_update_account(_, info, request):
    account_number = request["account_number"]
    fields_to_update, values = db.build_set_clause(
        ["account_type", "owner", "account_name"],
        request
    )

    if not fields_to_update:
        raise Exception("No fields provided to update.")

    values.append(account_number)  # for the WHERE clause

    query = f"""
        UPDATE account
        SET {", ".join(fields_to_update)}
        WHERE account_number = %s
        RETURNING account_number, account_type, owner, account_name
    """

    with get_cursor() as cur:
        cur.execute(query, values)
        row = cur.fetchone()
        cur.connection.commit()

    if not row:
        raise Exception("Account not found.")

    return {
        "account_number": row[0],
        "account_type": row[1],
        "owner": row[2],
        "account_name": row[3]
    }

@mutation.field("updateTransaction")
def resolve_update_transaction(_, info, request):
    transaction_id = request["transaction_id"]

    fields_to_update, values = db.build_set_clause(
        ["account_number", "date", "description_1", "description_2", "amount", "currency"],
        request
    )

    if not fields_to_update:
        raise Exception("No fields provided to update.")

    values.append(transaction_id)  # for the WHERE clause

    query = f"""
        UPDATE transactions
        SET {", ".join(fields_to_update)}
        WHERE transaction_id = %s
        RETURNING account_number, date, description_1, description_2, amount, currency, transaction_id
    """

    with get_cursor() as cur:
        cur.execute(query, values)
        row = cur.fetchone()
        cur.connection.commit()

    if not row:
        raise Exception("Transaction not found.")

    return {
        "account_number": row[0],
        "date": row[1],
        "description_1": row[2],
        "description_2": row[3],
        "amount": float(row[4]),
        "currency": row[5],
        "transaction_id": str(row[6])
    }

resolvers = [query, mutation, account_obj, transaction_obj]
