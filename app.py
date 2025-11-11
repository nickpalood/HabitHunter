from flask import Flask, render_template, redirect, url_for, request, flash
from models.data_manager import DataManager
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key

data_manager = DataManager('data/budget_data.json')


@app.route('/')
def dashboard():
    try:
        incomes = data_manager.get_incomes()
        expenses = data_manager.get_expenses()

        # Calculate totals
        total_income = sum([float(getattr(t, 'amount', 0.0)) for t in incomes])
        total_expenses = sum([float(getattr(t, 'amount', 0.0)) for t in expenses])
        balance = total_income - total_expenses

        # Get current date info
        now = datetime.now()
        current_month = now.strftime('%Y-%m')

        # Calculate last month (handle year rollover)
        if now.month == 1:
            last_month = f"{now.year - 1}-12"
        else:
            last_month = f"{now.year}-{str(now.month - 1).zfill(2)}"

        # Calculate current month totals
        current_month_income = 0
        current_month_expenses = 0
        last_month_income = 0
        last_month_expenses = 0

        for income in incomes:
            date_str = getattr(income, 'date', '')
            if date_str:
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    month_key = date_obj.strftime('%Y-%m')
                    amount = float(getattr(income, 'amount', 0))

                    if month_key == current_month:
                        current_month_income += amount
                    elif month_key == last_month:
                        last_month_income += amount
                except:
                    pass

        for expense in expenses:
            date_str = getattr(expense, 'date', '')
            if date_str:
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    month_key = date_obj.strftime('%Y-%m')
                    amount = float(getattr(expense, 'amount', 0))

                    if month_key == current_month:
                        current_month_expenses += amount
                    elif month_key == last_month:
                        last_month_expenses += amount
                except:
                    pass

        # Calculate trends
        income_trend = None
        income_trend_direction = 'neutral'
        if last_month_income > 0:
            income_change = ((current_month_income - last_month_income) / last_month_income) * 100
            income_trend = abs(income_change)
            income_trend_direction = 'up' if income_change > 0 else 'down'
        elif current_month_income > 0:
            income_trend = 100
            income_trend_direction = 'up'

        expense_trend = None
        expense_trend_direction = 'neutral'
        if last_month_expenses > 0:
            expense_change = ((current_month_expenses - last_month_expenses) / last_month_expenses) * 100
            expense_trend = abs(expense_change)
            expense_trend_direction = 'up' if expense_change > 0 else 'down'
        elif current_month_expenses > 0:
            expense_trend = 100
            expense_trend_direction = 'up'

        # Get recent transactions (combine income and expenses)
        recent_transactions = []

        for income in incomes:
            recent_transactions.append({
                'date': getattr(income, 'date', ''),
                'type': 'income',
                'category': getattr(income, 'category', ''),
                'amount': float(getattr(income, 'amount', 0))
            })

        for expense in expenses:
            recent_transactions.append({
                'date': getattr(expense, 'date', ''),
                'type': 'expense',
                'category': getattr(expense, 'category', ''),
                'amount': float(getattr(expense, 'amount', 0))
            })

        # Sort by date (most recent first) and get last 5
        recent_transactions.sort(key=lambda x: x['date'], reverse=True)
        recent_transactions = recent_transactions[:5]

        # Format dates for display
        for trans in recent_transactions:
            try:
                date_obj = datetime.strptime(trans['date'], '%Y-%m-%d')
                trans['formatted_date'] = date_obj.strftime('%B %d, %Y')
            except:
                trans['formatted_date'] = trans['date']

    except Exception as e:
        total_income = total_expenses = balance = 0.0
        income_trend = expense_trend = None
        income_trend_direction = expense_trend_direction = 'neutral'
        recent_transactions = []

    return render_template('dashboard.html',
                           total_income=total_income,
                           total_expenses=total_expenses,
                           balance=balance,
                           income_trend=income_trend,
                           income_trend_direction=income_trend_direction,
                           expense_trend=expense_trend,
                           expense_trend_direction=expense_trend_direction,
                           recent_transactions=recent_transactions)

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
    if request.method == 'POST':
        category = request.form.get('category')
        limit = request.form.get('limit')

        if not category or not limit:
            flash('Please fill in all fields!')
            return redirect(url_for('budgets'))

        try:
            limit = float(limit)
            if limit <= 0:
                raise ValueError("Limit must be positive")
        except ValueError:
            flash('Invalid limit amount!')
            return redirect(url_for('budgets'))

        # Create budget entry
        budget_entry = {
            'category': category,
            'limit': limit
        }

        # Check if budget already exists for this category
        existing = False
        for i, b in enumerate(data_manager._budgets):
            if getattr(b, 'category', None) == category:
                data_manager._budgets[i] = type('Budget', (), budget_entry)
                existing = True
                break

        if not existing:
            data_manager._budgets.append(type('Budget', (), budget_entry))

        data_manager.save()
        flash('Budget limit set successfully!')
        return redirect(url_for('budgets'))

    # Calculate spending per category
    expenses = data_manager.get_expenses()
    category_spending = {}

    for expense in expenses:
        cat = getattr(expense, 'category', 'Other')
        amount = float(getattr(expense, 'amount', 0))
        category_spending[cat] = category_spending.get(cat, 0) + amount

    # Prepare budget data with spending info
    budget_list = []
    for budget in data_manager.get_budgets():
        cat = getattr(budget, 'category', '')
        limit = float(getattr(budget, 'limit', 0))
        spent = category_spending.get(cat, 0)
        remaining = limit - spent
        percentage = (spent / limit * 100) if limit > 0 else 0

        budget_list.append({
            'category': cat,
            'limit': limit,
            'spent': spent,
            'remaining': remaining,
            'percentage': percentage
        })

    return render_template('budgets.html', budgets=budget_list)


@app.route('/delete_budget/<int:budget_id>', methods=['POST'])
def delete_budget(budget_id):
    try:
        del data_manager._budgets[budget_id]
        data_manager.save()
        flash('Budget deleted successfully!')
    except IndexError:
        flash('Budget not found!')
    return redirect(url_for('budgets'))


@app.route('/reports')
def reports():
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
    income_by_month = {}
    expense_by_month = {}

    for income in incomes:
        date_str = getattr(income, 'date', '')
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                # Use YYYY-MM as key for grouping, but store date object for sorting
                month_key = date_obj.strftime('%Y-%m')
                month_label = date_obj.strftime('%b %Y')
                amount = float(getattr(income, 'amount', 0))

                if month_key not in income_by_month:
                    income_by_month[month_key] = {'date': date_obj, 'label': month_label, 'amount': 0}
                income_by_month[month_key]['amount'] += amount
            except:
                pass

    for expense in expenses:
        date_str = getattr(expense, 'date', '')
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                month_label = date_obj.strftime('%b %Y')
                amount = float(getattr(expense, 'amount', 0))

                if month_key not in expense_by_month:
                    expense_by_month[month_key] = {'date': date_obj, 'label': month_label, 'amount': 0}
                expense_by_month[month_key]['amount'] += amount
            except:
                pass

    # Get all unique months and sort them
    all_month_keys = set(list(income_by_month.keys()) + list(expense_by_month.keys()))

    # Sort by the actual date, not alphabetically
    sorted_months = sorted(all_month_keys)

    # Build the data arrays
    month_labels = []
    income_trend = []
    expense_trend = []

    for month_key in sorted_months:
        # Get the label from either income or expense data
        if month_key in income_by_month:
            month_labels.append(income_by_month[month_key]['label'])
            income_trend.append(income_by_month[month_key]['amount'])
        elif month_key in expense_by_month:
            month_labels.append(expense_by_month[month_key]['label'])
            income_trend.append(0)

        if month_key in expense_by_month:
            expense_trend.append(expense_by_month[month_key]['amount'])
        else:
            expense_trend.append(0)

    monthly_data = len(sorted_months) > 0

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