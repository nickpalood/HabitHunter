from flask import Flask, render_template, redirect, url_for, request, flash
from models.data_manager import DataManager
from datetime import datetime

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
        # Get form data
        date = request.form.get('date')
        category = request.form.get('category')
        amount = request.form.get('amount')

        # Validate
        if not date or not category or not amount:
            flash('All fields are required!')
            return redirect(url_for('income'))

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError:
            flash('Invalid amount!')
            return redirect(url_for('income'))

        # Create income entry
        income_entry = {
            'date': date,
            'category': category,
            'amount': amount
        }

        # Add to data manager
        data_manager._incomes.append(type('Income', (), income_entry))

        flash('Income added successfully!')
        return redirect(url_for('income'))

    incomes = data_manager.get_incomes()
    return render_template('income.html', incomes=incomes)


@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
    if request.method == 'POST':
        # Get form data
        date = request.form.get('date')
        category = request.form.get('category')
        amount = request.form.get('amount')

        # Validate
        if not date or not category or not amount:
            flash('All fields are required!')
            return redirect(url_for('expenses'))

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError:
            flash('Invalid amount!')
            return redirect(url_for('expenses'))

        # Create expense entry
        expense_entry = {
            'date': date,
            'category': category,
            'amount': amount
        }

        # Add to data manager
        data_manager._expenses.append(type('Expense', (), expense_entry))

        flash('Expense added successfully!')
        return redirect(url_for('expenses'))

    expenses = data_manager.get_expenses()
    return render_template('expenses.html', expenses=expenses)


@app.route('/delete_income/<int:income_id>', methods=['POST'])
def delete_income(income_id):
    try:
        del data_manager._incomes[income_id]
        flash('Income deleted successfully!')
    except IndexError:
        flash('Income not found!')
    return redirect(url_for('income'))


@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    try:
        del data_manager._expenses[expense_id]
        flash('Expense deleted successfully!')
    except IndexError:
        flash('Expense not found!')
    return redirect(url_for('expenses'))


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
