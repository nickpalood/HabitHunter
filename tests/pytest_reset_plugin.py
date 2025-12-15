import pytest
import os
import database
from pathlib import Path


@pytest.fixture(scope="session", autouse=True)
def reset_test_data():
    print("\n" + "=" * 60)
    print("INITIALIZING TEST DATA RESET")
    print("=" * 60)
    
    database.init_db()
    print("[OK] Database initialized")
    
    database.drop_all_users_and_data()
    print("[OK] All database data cleared")
    merchant_files = [
        'data/merchant_category_expenses.json',
        'data/merchant_category_income.json'
    ]
    
    for filepath in merchant_files:
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"[OK] Removed: {filepath}")
            except Exception as e:
                print(f"[ERROR] Error removing {filepath}: {e}")
    
    print("=" * 60)
    print()
    yield
    print("\n" + "=" * 60)
    print("CLEANING UP TEST DATA")
    print("=" * 60)
    database.drop_all_users_and_data()
    print("[OK] Test data cleanup complete")
    print("=" * 60)


@pytest.fixture(autouse=True)
def reset_between_tests():
    if os.getenv('RESET_BETWEEN_TESTS', '0') == '1':
        database.drop_all_users_and_data()
        database.init_db()
        yield
        database.drop_all_users_and_data()
    else:
        yield
