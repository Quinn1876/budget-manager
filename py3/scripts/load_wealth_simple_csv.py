import argparse
import csv
import psycopg2
import logging
from dotenv import load_dotenv
from py3.lib import db

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("path", help="Relative Data path to csv file")
    parser.add_argument("--env_file", default=".env")
    account_number_group = parser.add_mutually_exclusive_group(required=True)
    account_number_group.add_argument("--account_number")
    account_number_group.add_argument("--account_number_file_path", help="Relative Path to file containing the account number")

    args = parser.parse_args()

    logger.debug("Loading Environment Variables...")
    assert load_dotenv(args.env_file), "Failed to load env file"

    logger.debug("Connecting to database...")
    conn = psycopg2.connect(dbname="budget_database", user="admin", password="password")
    cursor = conn.cursor()

    logger.debug("Checking if csv file has been processed before...")
    if db.get_csv_count(cursor, args.path) == 1:
        logger.error("CSV File %s has been processed already.", args.path)
        raise Exception(f"CSV File '{args.path}' already exists")

    logger.debug("Inserting %s into database...", args.path)
    db.insert_csv(cursor, args.path)

    rows = []

    with open(args.path) as csv_file:
        reader = csv.DictReader(csv_file, fieldnames=["date","transaction","description","amount","balance"])
        next(reader) # skip the header
        for entry in reader:
            rows.append(entry)

    existing_accounts = db.get_all_account_numbers(cursor)

    if args.account_number_file_path:
        with open(args.account_number_file_path, "r") as account_number_file:
            account_number = account_number_file.readline().strip("\n")
    else:
        account_number = args.account_number

    account: db.InsertAccount = {"account_number": account_number, "account_type": "Savings"}
    if account["account_number"] not in existing_accounts:
        logger.debug("Inserting account: %d, %s", account["account_number"], account["account_type"])
        db.insert_account(cursor, account)

    transactions: list[db.InsertTransaction] = list(map(lambda row: {
        "account_number": account_number,
        "date": row["date"],
        "description1": row["description"] ,
        "description2": row["transaction"],
        "amount": row["amount"],
        "currency": "CAD$"
    }, rows))

    for transaction in transactions:
        db.insert_transaction(cursor, transaction)

    conn.commit()



