import sqlite3
from database import get_db

class DataManager:
    def __init__(self, user_id=None):
        self.user_id = user_id
        self._incomes = []
        self._expenses = []
        self._budgets = []

    def set_user(self, user_id):
        """Set the current user and load their data"""
        self.user_id = user_id
        self.load()

    def load(self):
        """Load user data from database"""
        if not self.user_id:
            return
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Load incomes
            cursor.execute(
                'SELECT date, description, category, amount, currency FROM incomes WHERE user_id = ? ORDER BY date DESC',
                (self.user_id,)
            )
            self._incomes = [type('Income', (), dict(row)) for row in cursor.fetchall()]
            
            # Load expenses
            cursor.execute(
                'SELECT date, description, category, amount, currency FROM expenses WHERE user_id = ? ORDER BY date DESC',
                (self.user_id,)
            )
            self._expenses = [type('Expense', (), dict(row)) for row in cursor.fetchall()]
            
            # Load budgets
            cursor.execute(
                'SELECT category, limit_amount FROM budgets WHERE user_id = ?',
                (self.user_id,)
            )
            # Manually map limit_amount to 'limit' attribute for backward compatibility
            self._budgets = []
            for row in cursor.fetchall():
                budget_dict = dict(row)
                budget_dict['limit'] = budget_dict.pop('limit_amount')
                self._budgets.append(type('Budget', (), budget_dict))

    def save(self):
        """Save user data to database"""
        if not self.user_id:
            return
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Clear existing data for this user
            cursor.execute('DELETE FROM incomes WHERE user_id = ?', (self.user_id,))
            cursor.execute('DELETE FROM expenses WHERE user_id = ?', (self.user_id,))
            cursor.execute('DELETE FROM budgets WHERE user_id = ?', (self.user_id,))
            
            # Save incomes
            for income in self._incomes:
                cursor.execute(
                    'INSERT INTO incomes (user_id, date, description, category, amount, currency) VALUES (?, ?, ?, ?, ?, ?)',
                    (self.user_id, getattr(income, 'date'), getattr(income, 'description', ''),
                     getattr(income, 'category'), getattr(income, 'amount'), getattr(income, 'currency', 'EUR'))
                )
            
            # Save expenses
            for expense in self._expenses:
                cursor.execute(
                    'INSERT INTO expenses (user_id, date, description, category, amount, currency) VALUES (?, ?, ?, ?, ?, ?)',
                    (self.user_id, getattr(expense, 'date'), getattr(expense, 'description', ''),
                     getattr(expense, 'category'), getattr(expense, 'amount'), getattr(expense, 'currency', 'EUR'))
                )
            
            # Save budgets
            for budget in self._budgets:
                cursor.execute(
                    'INSERT INTO budgets (user_id, category, limit_amount) VALUES (?, ?, ?)',
                    (self.user_id, getattr(budget, 'category'), getattr(budget, 'limit'))
                )
            
            conn.commit()

    def get_incomes(self):
        return self._incomes

    def get_expenses(self):
        return self._expenses

    def get_budgets(self):
        return getattr(self, '_budgets', [])