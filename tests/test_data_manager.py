# DataManager tests
import pytest
from models.data_manager import DataManager
import database


@pytest.fixture
def dm():
    """Create a DataManager instance for testing."""
    dm = DataManager()
    user_id = database.create_user('testuser', 'password')
    dm.set_user(user_id)
    yield dm
    database.drop_all_users_and_data()


def test_data_manager_initialization():
    """Test DataManager initialization."""
    dm = DataManager()
    assert dm is not None
    assert hasattr(dm, 'user_id')


def test_set_user(dm):
    """Test setting user for DataManager."""
    assert dm.user_id is not None
    assert isinstance(dm.user_id, int)


def test_load_incomes(dm):
    """Test loading income transactions."""
    incomes = dm.get_incomes()
    assert isinstance(incomes, list)


def test_load_expenses(dm):
    """Test loading expense transactions."""
    expenses = dm.get_expenses()
    assert isinstance(expenses, list)


def test_load_budgets(dm):
    """Test loading budget data."""
    budgets = dm.get_budgets()
    assert isinstance(budgets, list)


def test_save_incomes(dm):
    """Test saving income transactions."""
    income = {
        'date': '2025-12-10',
        'category': 'Salary',
        'amount': 3000.0,
        'description': 'Monthly salary',
        'currency': 'EUR'
    }
    dm._incomes.append(type('Income', (), income)())
    dm.save()
    dm.load()
    incomes = dm.get_incomes()
    assert len(incomes) > 0


def test_save_expenses(dm):
    """Test saving expense transactions."""
    expense = {
        'date': '2025-12-10',
        'category': 'Food',
        'amount': 50.0,
        'description': 'Groceries',
        'currency': 'EUR'
    }
    dm._expenses.append(type('Expense', (), expense)())
    dm.save()
    dm.load()
    expenses = dm.get_expenses()
    assert len(expenses) > 0


def test_save_budgets(dm):
    """Test saving budget data."""
    budget = {
        'category': 'Food',
        'limit': 500.0
    }
    dm._budgets.append(type('Budget', (), budget)())
    dm.save()
    dm.load()
    budgets = dm.get_budgets()
    assert len(budgets) > 0


def test_get_incomes(dm):
    """Test retrieving income transactions."""
    income_dict = {
        'date': '2025-12-10',
        'category': 'Salary',
        'amount': 3000.0,
        'description': 'Monthly salary',
        'currency': 'EUR'
    }
    dm._incomes.append(type('Income', (), income_dict)())
    dm.save()
    dm.load()
    incomes = dm.get_incomes()
    assert len(incomes) == 1


def test_get_expenses(dm):
    """Test retrieving expense transactions."""
    expense_dict = {
        'date': '2025-12-10',
        'category': 'Food',
        'amount': 50.0,
        'description': 'Groceries',
        'currency': 'EUR'
    }
    dm._expenses.append(type('Expense', (), expense_dict)())
    dm.save()
    dm.load()
    expenses = dm.get_expenses()
    assert len(expenses) == 1


def test_get_budgets(dm):
    """Test retrieving budget data."""
    budget_dict = {
        'category': 'Food',
        'limit': 500.0
    }
    dm._budgets.append(type('Budget', (), budget_dict)())
    dm.save()
    dm.load()
    budgets = dm.get_budgets()
    assert len(budgets) == 1


def test_transaction_with_currency(dm):
    """Test transactions are saved with currency field."""
    income_dict = {
        'date': '2025-12-10',
        'category': 'Salary',
        'amount': 3000.0,
        'description': 'Monthly salary',
        'currency': 'GBP'
    }
    dm._incomes.append(type('Income', (), income_dict)())
    dm.save()
    dm.load()
    incomes = dm.get_incomes()
    assert len(incomes) == 1
    assert getattr(incomes[0], 'currency') == 'GBP'


def test_concurrent_user_data(dm):
    """Test data isolation between users."""
    income_dict = {
        'date': '2025-12-10',
        'category': 'Salary',
        'amount': 3000.0,
        'description': 'Monthly salary',
        'currency': 'EUR'
    }
    dm._incomes.append(type('Income', (), income_dict)())
    dm.save()
    dm.load()
    
    user_id2 = database.create_user('testuser2', 'password')
    dm2 = DataManager()
    dm2.set_user(user_id2)
    
    incomes1 = dm.get_incomes()
    incomes2 = dm2.get_incomes()
    
    assert len(incomes1) == 1
    assert len(incomes2) == 0


def test_data_consistency(dm):
    """Test data consistency after save/load cycle."""
    income_dict = {
        'date': '2025-12-10',
        'category': 'Salary',
        'amount': 3000.0,
        'description': 'Monthly salary',
        'currency': 'EUR'
    }
    dm._incomes.append(type('Income', (), income_dict)())
    dm.save()
    
    incomes1 = dm.get_incomes()
    
    dm2 = DataManager()
    dm2.set_user(dm.user_id)
    incomes2 = dm2.get_incomes()
    
    assert len(incomes1) == len(incomes2)
