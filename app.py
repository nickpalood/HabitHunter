from flask import Flask, render_template, redirect, url_for, request, flash
from models.data_manager import DataManager

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key

data_manager = DataManager('data/budget_data.json')

@app.route('/')
def dashboard():
    # Example: get summary data for dashboard
    try:
        total_income = sum([float(getattr(t, 'amount', 0.0)) for t in data_manager.get_incomes()])
        total_expenses = sum([float(getattr(t, 'amount', 0.0)) for t in data_manager.get_expenses()])
        balance = total_income - total_expenses
    except Exception:
        total_income = total_expenses = balance = 0.0
    return render_template('dashboard.html', total_income=total_income, total_expenses=total_expenses, balance=balance)

@app.route('/income', methods=['GET', 'POST'])
def income():
    if request.method == 'POST':
        # Handle new income entry
        # ... implement form handling ...
        flash('Income added!')
        return redirect(url_for('income'))
    incomes = data_manager.get_incomes()
    return render_template('income.html', incomes=incomes)

@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
    if request.method == 'POST':
        # Handle new expense entry
        # ... implement form handling ...
        flash('Expense added!')
        return redirect(url_for('expenses'))
    expenses = data_manager.get_expenses()
    return render_template('expenses.html', expenses=expenses)

@app.route('/budgets', methods=['GET', 'POST'])
def budgets():
    # Implement budget logic
    return render_template('budgets.html')

@app.route('/reports')
def reports():
    # Implement reports logic
    return render_template('reports.html')

@app.route('/save')
def save():
    try:
        data_manager.save()
        flash('Data saved successfully!')
    except Exception as e:
        flash(f'Error saving data: {e}')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5002)
