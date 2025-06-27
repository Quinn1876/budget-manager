import uuid
from ariadne import QueryType, MutationType, ObjectType
from py3.lib import db
from py3.lib.db import get_cursor

query = QueryType()
mutation = MutationType()
account_obj = ObjectType("Account")
transaction_obj = ObjectType("Transaction")
owner_summary_obj = ObjectType("OwnerSummary")

def row_to_account(row):
    return {
        "account_number": row[0],
        "account_type": row[1],
        "owner": row[2],
        "account_name": row[3],
        "initial_balance": row[4]
    }

def row_to_transaction(row):
    return {
        "account_number": row[0],
        "date": str(row[1]),
        "description_1": row[2],
        "description_2": row[3],
        "amount": float(row[4]),
        "currency": row[5].strip(),
        "transaction_id": str(row[6])
    }

@query.field("listAccounts")
def resolve_accounts(*_):
    with get_cursor() as cur:
        cur.execute("SELECT account_number, account_type, owner, account_name, initial_balance FROM account")
        return [
            row_to_account(row)
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
            row_to_transaction(row)
            for row in cur.fetchall()
        ]

@query.field("getTransaction")
def resolve_transaction(_, info, transaction_id):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM transactions WHERE transaction_id = %s", (transaction_id,))
        row = cur.fetchone()
        if row:
            return row_to_transaction(row)

@query.field("getOwnerSummary")
def resolve_owner_summary(_, _info, owner):
    return {
        "owner": owner
    }


@transaction_obj.field("account")
def resolve_transaction_account(obj, *_):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM account WHERE account_number = %s", (obj["account_number"],))
        row = cur.fetchone()
        if row:
            return row_to_account(row)

@account_obj.field("transactions")
def resolve_account_transactions(obj, *_):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM transactions WHERE account_number = %s", (obj["account_number"],))
        return [
            row_to_transaction(row)
            for row in cur.fetchall()
        ]

@account_obj.field("balance")
def resolve_account_balance(obj, *_):
    with get_cursor() as cur:
        cur.execute("SELECT sum(t.amount) as balance FROM transactions as t WHERE t.account_number = %s", (obj["account_number"],))
        row = cur.fetchone()
        if row:
            return row[0] + obj["initial_balance"]

@owner_summary_obj.field("accounts")
def resolve_owner_summary_accounts(obj, *_):
    owner = obj["owner"]
    with get_cursor() as cur:
        cur.execute("SELECT account_number, account_type, owner, account_name, initial_balance FROM account WHERE owner = %s", (owner,))
        return [
            row_to_account(row)
            for row in cur.fetchall()
        ]

@owner_summary_obj.field("total_savings")
def resolve_owner_summary_total_savings(obj, *_):
    owner = obj["owner"]
    with get_cursor() as cur:
        initial_balance = 0
        cur.execute("SELECT sum(initial_balance) from account where owner = %s and account_type = 'Savings'", (owner,))
        row = cur.fetchone()
        if row:
            initial_balance = row[0]
        cur.execute("SELECT sum(t.amount) FROM transactions as t INNER JOIN account as a ON t.account_number = a.account_number WHERE a.owner = %s and a.account_type = 'Savings'", (owner,))
        row = cur.fetchone()
        if row:
            return row[0] + initial_balance


@owner_summary_obj.field("total_dept")
def resolve_owner_summary_total_dept(obj, *_):
    owner = obj["owner"]
    with get_cursor() as cur:
        initial_balance = 0
        cur.execute("SELECT sum(initial_balance) from account where owner = %s and account_type <> 'Savings'", (owner,))
        row = cur.fetchone()
        if row:
            initial_balance = row[0]
        cur.execute("SELECT sum(t.amount) FROM transactions as t INNER JOIN account as a ON t.account_number = a.account_number WHERE a.owner = %s and a.account_type <> 'Savings'", (owner,))
        row = cur.fetchone()
        if row:
            return row[0] + initial_balance


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
def resolve_update_account(_, info, **request):
    account_number = request["account_number"]
    fields_to_update, values = db.build_set_clause(
        ["account_type", "owner", "account_name", "initial_balance"],
        request["input"]
    )

    if not fields_to_update:
        raise Exception("No fields provided to update.")

    values.append(account_number)  # for the WHERE clause

    query = f"""
        UPDATE account
        SET {", ".join(fields_to_update)}
        WHERE account_number = %s
        RETURNING account_number, account_type, owner, account_name, initial_balance
    """

    with get_cursor() as cur:
        cur.execute(query, values)
        row = cur.fetchone()
        cur.connection.commit()

    if not row:
        raise Exception("Account not found.")

    return row_to_account(row)

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

    return row_to_transaction(row)

resolvers = [query, mutation, account_obj, transaction_obj, owner_summary_obj]
