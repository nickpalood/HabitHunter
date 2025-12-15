import pytest
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app as flask_app
from models.data_manager import DataManager
import database


@pytest.fixture(scope="session", autouse=True)
def reset_test_data_on_startup():
    print("\n" + "=" * 60)
    print("INITIALIZING TEST ENVIRONMENT")
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
    try:
        database.drop_all_users_and_data()
        print("[OK] Test data cleanup complete")
    except Exception as e:
        print(f"[ERROR] Error during cleanup: {e}")
    print("=" * 60)


@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    flask_app.config['SECRET_KEY'] = 'test_secret_key'
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def init_database():
    database.init_db()
    yield
    database.drop_all_users_and_data()

@pytest.fixture
def authenticated_client(client, init_database):
    client.post('/signup', data={
        'username': 'testuser',
        'password': 'testpass',
        'confirm_password': 'testpass'
    })
    yield client
    
@pytest.fixture
def data_manager():
    dm = DataManager()
    yield dm

@pytest.fixture
def sample_income():
    return {
        'date': '2025-12-10',
        'category': 'Salary',
        'amount': 3000.0,
        'description': 'Monthly salary',
        'currency': 'EUR'
    }

@pytest.fixture
def sample_expense():
    return {
        'date': '2025-12-12',
        'category': 'Food & Dining',
        'amount': 50.0,
        'description': 'Groceries',
        'currency': 'EUR'
    }

@pytest.fixture
def sample_budget():
    return {
        'category': 'Food & Dining',
        'limit': 500.0
    }