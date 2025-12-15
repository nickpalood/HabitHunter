# Habit Hunter

A comprehensive personal finance management web app built with Flask. Track income and expenses across multiple currencies, set monthly budgets, auto-categorize transactions using merchant mapping, and analyze spending patterns with advanced analytics.

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd simple-budget-tracker

# Install dependencies
pip install -r requirements.txt
```

### Running the App
```bash
python app.py
```
The app will start on `http://localhost:5002` in debug mode.

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run with verbose output
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_expenses.py -v
```

### Resetting Test Data
```bash
python reset_for_testing.py
```
This clears all user data and merchant mappings for a clean test environment.

## Core Features

### Authentication & User Management
- User registration with hashed passwords (SHA-256)
- Secure login/logout with session management
- User-isolated data storage

### Income & Expense Tracking
- Add income and expense transactions with date, description, category, and amount
- Support for multiple currencies (EUR, USD, GBP, etc.)
- Automatic currency conversion to EUR
- Edit and delete transactions
- Track merchant names for auto-categorization

### Merchant Auto-Categorization
- Intelligent merchant-to-category mapping system
- Two JSON mapping files: merchant_category_expenses.json and merchant_category_income.json
- Auto-categorize transactions based on merchant name
- Learn from user categorization patterns
- Manual category changes update merchant mappings

### Budget Management
- Set monthly spending limits per expense category
- Track budget progress with visual indicators
- Unique budget per user and category
- Real-time budget vs. actual spending comparison

### Financial Reports
- Monthly spending summary by category
- Income vs. expense comparison
- Category-wise breakdown
- Recent transaction history
- Financial overview dashboard

### Advanced Analytics (Graphs & Stats)
- Spending patterns by day of week
- Category performance analysis
- Monthly income/expense trends
- Statistical measures (average, max, min spending)
- Spending predictions for next 3 months
- Yearly balance forecasts using linear regression

### Revolut Transaction Import
- Import transactions from Revolut CSV exports
- Batch import with automatic date parsing
- Currency support maintained during import
- Auto-categorization applied to imported transactions

### Dashboard
- Real-time balance display
- Monthly spending chart
- Quick access to all features
- Multi-timeframe view (1, 3, 6, 12 months)
- Currency selector for preferred display currency

## Data Storage

### SQLite Database (`data/budget_tracker.db`)
- **Users table**: Username, password hash, creation timestamp
- **Expenses table**: User ID, date, description, category, amount, currency, timestamp
- **Incomes table**: User ID, date, description, category, amount, currency, timestamp
- **Budgets table**: User ID, category, spending limit, unique constraint per user-category

### Merchant Mappings (JSON)
- **merchant_category_expenses.json**: Maps merchant names to expense categories
- **merchant_category_income.json**: Maps merchant names to income categories
- Auto-created if missing when app starts
- Updated when users change transaction categories

## Testing

### Running Tests
```bash
# Run all tests (207 tests across 12 test files)
python -m pytest tests/

# Run with verbose output (shows each test)
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_expenses.py -v

# Run specific test
python -m pytest tests/test_database.py::test_init_db -v

# Run with detailed output on failures
python -m pytest tests/ --tb=short
```

### Reset Test Data
```bash
python reset_for_testing.py
```
This clears the SQLite database and merchant mapping files for a fresh test environment.

**Note:** The test suite automatically resets the database before running, ensuring an isolated test environment.

### Test Coverage
- Database operations (users, transactions, budgets)
- User authentication and session handling
- Currency conversion and formatting
- Transaction categorization and merchant mapping
- Income and expense operations
- Budget creation and tracking
- Report generation and calculations
- Graph data and statistical analysis
- Revolut CSV import parsing
- Edge cases and error handling

## Project Structure
```
├── app.py                           # Main Flask app (1096 lines)
│                                      Routes: /, /login, /signup, /logout, /dashboard,
│                                      /income, /expenses, /budgets, /reports,
│                                      /graphs-stats, /revolut_import
│
├── database.py                      # SQLite operations
│                                      Tables: users, expenses, incomes, budgets
│                                      Auth: password hashing, user management
│
├── merchant_mapper.py               # Auto-categorization system
│                                      Load/save merchant mappings
│                                      Auto-categorize based on merchant name
│
├── currency_converter.py            # Multi-currency support
│                                      Currency conversion to EUR
│                                      Amount formatting
│
├── models/
│   └── data_manager.py             # Data management layer
│                                      Load/save user transactions
│                                      In-memory data manipulation
│
├── api/
│   └── revolut_importer.py         # Revolut CSV import
│                                      Parse CSV transactions
│                                      Handle date/amount parsing
│
├── static/                         # CSS stylesheets
│   ├── base.css                    # Base styles
│   ├── dashboard.css               # Dashboard styling
│   ├── income.css
│   ├── expenses.css
│   ├── budgets.css
│   ├── graphs.css
│   └── reports.css
│
├── templates/                      # Jinja2 HTML templates
│   ├── dashboard.html              # Main dashboard
│   ├── income.html                 # Income tracking
│   ├── expenses.html               # Expense tracking
│   ├── budgets.html                # Budget management
│   ├── reports.html                # Financial reports
│   ├── graphs_stats.html           # Analytics and predictions
│   ├── login.html                  # Login page
│   ├── signup.html                 # Registration page
│   └── revolut_import.html         # CSV import page
│
├── data/                          # Data storage (auto-created)
│   ├── budget_tracker.db          # SQLite database
│   ├── merchant_category_expenses.json
│   └── merchant_category_income.json
│
├── tests/                         # 207 unit tests
│   ├── conftest.py                # Pytest fixtures and auto-reset
│   ├── test_database.py           # Database operations
│   ├── test_user_authentication.py # Auth tests
│   ├── test_currency_converter.py # Currency tests
│   ├── test_income.py             # Income operations
│   ├── test_expenses.py           # Expense operations
│   ├── test_budgets.py            # Budget tests
│   ├── test_reports.py            # Report generation
│   ├── test_graphs_stats.py       # Analytics tests
│   ├── test_data_manager.py       # Data layer tests
│   ├── test_merchant_mapper.py    # Categorization tests
│   ├── test_revolut_importer.py   # Import tests
│   ├── test_routes.py             # Route tests
│   ├── test_edge_cases.py         # Edge case handling
│   └── test_helper_functions.py   # Utility tests
│
├── reset_for_testing.py           # Test data cleanup utility
├── requirements.txt               # Python dependencies
└── README.md
```

## Technology Stack
- **Backend**: Python 3.14, Flask 3.0+
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, JavaScript
- **Data Format**: JSON (merchant mappings)
- **Testing**: pytest with session-scoped fixtures
- **Authentication**: SHA-256 password hashing
- **API**: CSV import, Currency conversion


