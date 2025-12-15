import sqlite3
import hashlib
import os
from pathlib import Path
from contextlib import contextmanager

DATABASE_PATH = 'data/budget_tracker.db'

def ensure_data_directory_exists():
    """Ensure data directory exists"""
    os.makedirs('data', exist_ok=True)

@contextmanager
def get_db():
    """Context manager for database connections"""
    ensure_data_directory_exists()
    conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Initialize the database with required tables"""
    ensure_data_directory_exists()
    conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
    cursor = conn.cursor()
    
    try:
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Expenses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'EUR',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Incomes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS incomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'EUR',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Budgets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                limit_amount REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, category),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Migration: Add currency column to expenses and incomes tables if it doesn't exist
        cursor.execute("PRAGMA table_info(expenses)")
        expenses_columns = [col[1] for col in cursor.fetchall()]
        if 'currency' not in expenses_columns:
            cursor.execute('ALTER TABLE expenses ADD COLUMN currency TEXT DEFAULT "EUR"')
        
        cursor.execute("PRAGMA table_info(incomes)")
        incomes_columns = [col[1] for col in cursor.fetchall()]
        if 'currency' not in incomes_columns:
            cursor.execute('ALTER TABLE incomes ADD COLUMN currency TEXT DEFAULT "EUR"')
        
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise RuntimeError(f"Database initialization failed: {e}")
    finally:
        cursor.close()
        conn.close()

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify a password against its hash"""
    return hash_password(password) == password_hash

def create_user(username, password):
    """Create a new user"""
    with get_db() as conn:
        cursor = conn.cursor()
        password_hash = hash_password(password)
        try:
            cursor.execute(
                'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                (username, password_hash)
            )
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

def authenticate_user(username, password):
    """Authenticate a user and return user_id if successful"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, password_hash FROM users WHERE username = ?',
            (username,)
        )
        user = cursor.fetchone()
        if user and verify_password(password, user['password_hash']):
            return user['id']
        return None

def get_user_by_id(user_id):
    """Get user information by user_id"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, password_hash FROM users WHERE id = ?', (user_id,))
        return cursor.fetchone()

def drop_all_users_and_data():
    """Drop all users and their associated data from the database"""
    conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
    cursor = conn.cursor()
    
    try:
        # Delete all data from all tables (order matters due to foreign keys)
        cursor.execute('DELETE FROM budgets')
        cursor.execute('DELETE FROM incomes')
        cursor.execute('DELETE FROM expenses')
        cursor.execute('DELETE FROM users')
        # Reset autoincrement counters
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('users', 'expenses', 'incomes', 'budgets')")
        conn.commit()
        print("All users and associated data have been dropped from the database.")
    except sqlite3.Error as e:
        conn.rollback()
        raise RuntimeError(f"Failed to clear database data: {e}")
    finally:
        cursor.close()
        conn.close()
