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
    from collections import defaultdict
    from datetime import datetime

    # Get all transactions
    incomes = data_manager.get_incomes()
    expenses = data_manager.get_expenses()

    # Calculate totals
    total_income = sum([float(getattr(t, 'amount', 0)) for t in incomes])
    total_expenses = sum([float(getattr(t, 'amount', 0)) for t in expenses])
    balance = total_income - total_expenses

    # Expenses by category
    category_totals = defaultdict(float)
    for expense in expenses:
        cat = getattr(expense, 'category', 'Other')
        amount = float(getattr(expense, 'amount', 0))
        category_totals[cat] += amount

    expense_by_category = []
    category_labels = []
    category_values = []

    for cat, amount in category_totals.items():
        percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
        expense_by_category.append({
            'category': cat,
            'amount': amount,
            'percentage': percentage
        })
        category_labels.append(cat)
        category_values.append(amount)

    # Monthly trends
    income_by_month = defaultdict(float)
    expense_by_month = defaultdict(float)

    for income in incomes:
        date_str = getattr(income, 'date', '')
        if date_str:
            try:
                month = datetime.strptime(date_str, '%Y-%m-%d').strftime('%b %Y')
                amount = float(getattr(income, 'amount', 0))
                income_by_month[month] += amount
            except:
                pass

    for expense in expenses:
        date_str = getattr(expense, 'date', '')
        if date_str:
            try:
                month = datetime.strptime(date_str, '%Y-%m-%d').strftime('%b %Y')
                amount = float(getattr(expense, 'amount', 0))
                expense_by_month[month] += amount
            except:
                pass

    # Get all unique months and sort them
    all_months = sorted(set(list(income_by_month.keys()) + list(expense_by_month.keys())))
    month_labels = all_months
    income_trend = [income_by_month.get(m, 0) for m in all_months]
    expense_trend = [expense_by_month.get(m, 0) for m in all_months]

    monthly_data = len(all_months) > 0

    # Recent transactions (last 10)
    recent_transactions = []

    for income in incomes:
        recent_transactions.append({
            'date': getattr(income, 'date', ''),
            'type': 'Income',
            'category': getattr(income, 'category', ''),
            'amount': float(getattr(income, 'amount', 0))
        })

    for expense in expenses:
        recent_transactions.append({
            'date': getattr(expense, 'date', ''),
            'type': 'Expense',
            'category': getattr(expense, 'category', ''),
            'amount': float(getattr(expense, 'amount', 0))
        })

    # Sort by date and get last 10
    recent_transactions.sort(key=lambda x: x['date'], reverse=True)
    recent_transactions = recent_transactions[:10]

    return render_template('reports.html',
                           total_income=total_income,
                           total_expenses=total_expenses,
                           balance=balance,
                           expense_by_category=expense_by_category,
                           category_labels=category_labels,
                           category_values=category_values,
                           monthly_data=monthly_data,
                           month_labels=month_labels,
                           income_trend=income_trend,
                           expense_trend=expense_trend,
                           recent_transactions=recent_transactions)

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
