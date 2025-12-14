# Simple Budget Tracker

A web-based budget tracking application. Track your income and expenses, set spending limits, and see where your money goes with charts and analytics.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Team](#team)
- [Technologies](#technologies)
- [Contributing](#contributing)
- [License](#license)

## Features

### Main Features
- Track income from multiple sources
- Log expenses across different categories
- Set monthly spending limits for each category
- View financial reports with charts
- Get spending predictions based on your history
- All data stored locally on your computer

### Income Categories
Salary, Freelance, Business, Investment Returns, Rental Income, Side Hustle, Gift/Bonus, Refund, Interest, Other

### Expense Categories
Food & Dining, Transportation, Utilities, Rent/Mortgage, Entertainment, Shopping, Healthcare, Education, Insurance, Other

## Installation

### Requirements
Python 3.8 or higher and pip

### Setup

1. **Note**: This is a private school project repository on git.liacs.leidenuniv.nl. Access requires university credentials.

2. Install Flask
   ```bash
   pip install flask
   ```

3. Run the application
   ```bash
   python app.py
   ```

4. Open in your browser at `http://localhost:5000` (default Flask port)

   **Note**: The port may vary. Check the Flask output in your terminal.

### Troubleshooting

**Port already in use?**
Change the port in `app.py` (line at the bottom):
```python
app.run(debug=True, port=5003)  # Change to any available port
```

**Flask not found?**
Make sure you installed Flask correctly:
```bash
python -m pip install flask
```

## Usage

### Adding Income
1. Go to the Income tab
2. Select the date and category
3. Enter the amount and optional description
4. Click Add Income

### Adding Expenses
1. Go to the Expenses tab
2. Select the date and category
3. Enter the amount and optional description
4. Click Add Expense

### Setting Budgets
1. Go to the Budgets tab
2. Choose a category and enter your monthly limit
3. Click Create Budget
4. Monitor spending with the progress bars

### Viewing Reports
The Reports tab shows your financial summary, spending by category, monthly trends, and recent transactions.

### Analyzing with Graphs & Stats
The Graphs & Stats tab provides advanced analytics including:
- Spending patterns by day of week
- Category performance breakdowns
- Monthly income and expense trends
- Statistical analysis (average, max, min spending)
- Spending predictions for the next 3 months
- Yearly balance forecasts

### Data Storage
All data is currently stored in memory and will be lost when the application closes. File persistence (JSON storage) is planned for future versions.

## Project Structure

```
simple-budget-tracker/
├── app.py                      # Main Flask application
├── README.md                   # This file
│
├── templates/                  # HTML templates (Jinja2)
│   ├── dashboard.html          # Main overview with balance and expense chart
│   ├── income.html             # Add/view income entries
│   ├── expenses.html           # Add/view expense entries
│   ├── budgets.html            # Set and monitor spending limits
│   ├── reports.html            # Financial reports with charts
│   └── graphs_stats.html       # Advanced analytics and predictions
│
├── static/                     # CSS stylesheets
│   └── base.css                # Main stylesheet (all pages)
│
├── models/
│   ├── __init__.py
│   └── data_manager.py         # In-memory data storage
│
├── data/                       # Data storage directory (created at runtime)
│   └── __init__.py
│
└── documentation/              # This documentation
```

## About This Project

This is a school project built for the Software Development course at Leiden University. It's a collaborative effort by a team of 6 developers to create a practical budget tracking application.

**Repository**: Private repository on git.liacs.leidenuniv.nl (university credentials required)

**Team Members**: Nick (UI Design), Alberto (Income/Expenses), WARD (Data Models), Oswin (Budgets & Reports), Ronny (Utilities), Karim (Testing & Integration)

## Technologies

Backend: Flask 3.0+, Python 3.8+
Frontend: HTML5, CSS3, JavaScript
Charts: Chart.js 4.4.0
Data: JSON storage

## Contributing

Since this is a private school project, contributions are managed through the university's git.liacs platform. Team members should follow the developer guide for workflow and coding standards.

---