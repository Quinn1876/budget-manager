import argparse
import csv
from datetime import datetime
import os
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
        reader = csv.DictReader(csv_file, fieldnames=["Account Type","Account Number","Transaction Date","Cheque Number","Description 1","Description 2","CAD$","USD$"])
        next(reader) # skip the header
        for entry in reader:
            rows.append(entry)

    existing_accounts = db.get_all_account_numbers(cursor)
    accounts: list[db.InsertAccount] = list(map(lambda row: { "account_number": row["Account Number"], "account_type": row["Account Type"] }, rows))
    for account in accounts:
        if account["account_number"] not in existing_accounts:
            existing_accounts.add(account["account_number"])
            logger.debug("Inserting account: %d, %s", account["account_number"], account["account_type"])
            db.insert_account(cursor, account)

    transactions: list[db.InsertTransaction] = list(map(lambda row: {
        "account_number": row["Account Number"],
        "date": datetime.strptime(row["Transaction Date"], '%m/%d/%Y').strftime("%Y-%m-%d"),
        "description1": row["Description 1"] ,
        "description2": row["Description 2"],
        "amount": row["CAD$"] if row["CAD$"] is not None else row["USD$"],
        "currency": "CAD$" if row["CAD$"] is not None else "USD$"
    }, rows))

    for transaction in transactions:
        db.insert_transaction(cursor, transaction)

    conn.commit()



