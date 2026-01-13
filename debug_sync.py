#!/usr/bin/env python3
"""Debug script to test YNAB sync and identify issues."""

import sys
import traceback

# Add project to path
sys.path.insert(0, '.')

from src.utils.config import get_token_from_secrets
from src.api.ynab_client import YNABClient
from src.cache.database import Database
from src.cache.sync import SyncManager

def main():
    print("=" * 60)
    print("YNAB Sync Debug Script")
    print("=" * 60)

    # Get token
    print("\n[1] Loading API token...")
    token = get_token_from_secrets()
    if not token:
        print("ERROR: No token found in .streamlit/secrets.toml")
        return
    print(f"    Token loaded: {token[:8]}...{token[-4:]}")

    # Initialize client
    print("\n[2] Initializing YNAB client...")
    client = YNABClient(token)

    # Test connection
    print("\n[3] Testing connection...")
    if client.test_connection():
        print("    Connection OK")
    else:
        print("    ERROR: Connection failed")
        return

    # Get budgets
    print("\n[4] Fetching budgets...")
    try:
        budgets = client.get_budgets()
        for b in budgets:
            print(f"    - {b.name} ({b.id})")
        budget_id = budgets[0].id
        print(f"    Using budget: {budget_id}")
    except Exception as e:
        print(f"    ERROR: {e}")
        traceback.print_exc()
        return

    # Initialize database
    print("\n[5] Initializing database...")
    db = Database()
    print(f"    Database path: {db.db_path}")

    # Test transaction fetch directly
    print("\n[6] Testing transaction fetch from API...")
    try:
        transactions, knowledge = client.get_transactions(budget_id)
        print(f"    SUCCESS: Got {len(transactions)} transactions")
        print(f"    Server knowledge: {knowledge}")
        if transactions:
            print(f"    Sample transaction:")
            t = transactions[0]
            print(f"      - ID: {t.id}")
            print(f"      - Date: {t.var_date}")
            print(f"      - Payee: {t.payee_name}")
            print(f"      - Amount: {t.amount}")
            print(f"      - Category: {t.category_name}")
    except Exception as e:
        print(f"    ERROR fetching transactions: {e}")
        traceback.print_exc()
        return

    # Test inserting a transaction
    print("\n[7] Testing transaction insert to database...")
    try:
        if transactions:
            t = transactions[0]
            db.upsert_transaction(
                txn_id=t.id,
                budget_id=budget_id,
                account_id=t.account_id,
                account_name=t.account_name,
                txn_date=str(t.var_date),
                amount=t.amount,
                memo=t.memo,
                cleared=t.cleared,
                approved=t.approved,
                flag_color=t.flag_color,
                payee_id=t.payee_id,
                payee_name=t.payee_name,
                category_id=t.category_id,
                category_name=t.category_name,
                transfer_account_id=t.transfer_account_id,
                transfer_transaction_id=t.transfer_transaction_id,
                import_id=t.import_id,
                deleted=t.deleted
            )
            print("    SUCCESS: Transaction inserted")
    except Exception as e:
        print(f"    ERROR inserting transaction: {e}")
        traceback.print_exc()
        return

    # Run full sync
    print("\n[8] Running full sync via SyncManager...")
    try:
        sync = SyncManager(db, client)
        stats = sync.sync_budget(budget_id, force_full=True)
        print(f"    Results:")
        print(f"      - Accounts: {stats['accounts']}")
        print(f"      - Categories: {stats['categories']}")
        print(f"      - Transactions: {stats['transactions']}")
        print(f"      - Scheduled: {stats['scheduled_transactions']}")
        if stats['errors']:
            print(f"    ERRORS:")
            for err in stats['errors']:
                print(f"      - {err}")
    except Exception as e:
        print(f"    ERROR during sync: {e}")
        traceback.print_exc()
        return

    # Verify database
    print("\n[9] Verifying database contents...")
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM transactions")
    count = cursor.fetchone()[0]
    print(f"    Transactions in database: {count}")
    conn.close()

    print("\n" + "=" * 60)
    print("Debug complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
