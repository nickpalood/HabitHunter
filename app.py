from flask import Flask, render_template, redirect, url_for, request, flash
from models.data_manager import DataManager
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key

data_manager = DataManager('data/budget_data.json')


def linear_regression(x_values, y_values):
    """Simple linear regression using least squares method"""
    if len(x_values) < 2 or len(y_values) < 2:
        return None, None
    
    n = len(x_values)
    mean_x = sum(x_values) / n
    mean_y = sum(y_values) / n
    
    numerator = sum((x_values[i] - mean_x) * (y_values[i] - mean_y) for i in range(n))
    denominator = sum((x_values[i] - mean_x) ** 2 for i in range(n))
    
    if denominator == 0:
        return None, None
    
    slope = numerator / denominator
    intercept = mean_y - slope * mean_x
    
    return slope, intercept


def predict_value(slope, intercept, x):
    """Predict a value using linear regression"""
    if slope is None or intercept is None:
        return None
    return slope * x + intercept


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

        # Calculate expenses by category for chart
        expense_by_category = defaultdict(float)
        for expense in expenses:
            category = getattr(expense, 'category', 'Other')
            amount = float(getattr(expense, 'amount', 0))
            expense_by_category[category] += amount

        category_labels = list(expense_by_category.keys())
        category_values = list(expense_by_category.values())

    except Exception as e:
        total_income = total_expenses = balance = 0.0
        income_trend = expense_trend = None
        income_trend_direction = expense_trend_direction = 'neutral'
        recent_transactions = []
        category_labels = []
        category_values = []

    return render_template('dashboard.html',
                           total_income=total_income,
                           total_expenses=total_expenses,
                           balance=balance,
                           income_trend=income_trend,
                           income_trend_direction=income_trend_direction,
                           expense_trend=expense_trend,
                           expense_trend_direction=expense_trend_direction,
                           recent_transactions=recent_transactions,
                           category_labels=category_labels,
                           category_values=category_values)

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



@app.route('/graphs-stats')
def graphs_stats():
    """Comprehensive analytics and visualization dashboard with predictions"""
    try:
        incomes = data_manager.get_incomes()
        expenses = data_manager.get_expenses()

        # Calculate totals
        total_income = sum([float(getattr(t, 'amount', 0)) for t in incomes])
        total_expenses = sum([float(getattr(t, 'amount', 0)) for t in expenses])
        balance = total_income - total_expenses

        # ===== SPENDING BY CATEGORY =====
        category_totals = defaultdict(float)
        category_counts = defaultdict(int)
        for expense in expenses:
            cat = getattr(expense, 'category', 'Other')
            amount = float(getattr(expense, 'amount', 0))
            category_totals[cat] += amount
            category_counts[cat] += 1

        category_labels = list(category_totals.keys())
        category_values = list(category_totals.values())

        # Top 5 categories
        top_cats = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        top_cat_names = [cat for cat, _ in top_cats]
        top_cat_values = [val for _, val in top_cats]

        # ===== SPENDING BY DAY OF WEEK =====
        day_spending = defaultdict(float)
        day_transaction_counts = defaultdict(int)
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for expense in expenses:
            date_str = getattr(expense, 'date', '')
            if date_str:
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    day_name = day_order[date_obj.weekday()]
                    amount = float(getattr(expense, 'amount', 0))
                    day_spending[day_name] += amount
                    day_transaction_counts[day_name] += 1
                except:
                    pass

        # Ensure all days are represented
        day_labels = day_order
        day_values = [day_spending.get(day, 0) for day in day_order]
        day_transaction_counts_list = [day_transaction_counts.get(day, 0) for day in day_order]

        # ===== MONTHLY TRENDS =====
        income_by_month = {}
        expense_by_month = {}

        for income in incomes:
            date_str = getattr(income, 'date', '')
            if date_str:
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
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

        all_month_keys = set(list(income_by_month.keys()) + list(expense_by_month.keys()))
        sorted_months = sorted(all_month_keys)

        month_labels = []
        income_trend = []
        expense_trend = []

        for month_key in sorted_months:
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

        # ===== DAILY SPENDING THROUGHOUT MONTH =====
        date_spending = defaultdict(float)
        for expense in expenses:
            date_str = getattr(expense, 'date', '')
            if date_str:
                amount = float(getattr(expense, 'amount', 0))
                date_spending[date_str] += amount

        sorted_dates = sorted(date_spending.keys())
        date_labels = sorted_dates
        date_values = [date_spending[date] for date in sorted_dates]

        # ===== STATISTICS =====
        all_amounts = [float(getattr(e, 'amount', 0)) for e in expenses]
        avg_expense = sum(all_amounts) / len(all_amounts) if all_amounts else 0
        max_expense = max(all_amounts) if all_amounts else 0
        min_expense = min(all_amounts) if all_amounts else 0

        all_income_amounts = [float(getattr(i, 'amount', 0)) for i in incomes]
        avg_income = sum(all_income_amounts) / len(all_income_amounts) if all_income_amounts else 0

        # Calculate average daily spending
        total_days = len(set([getattr(e, 'date', '') for e in expenses]))
        avg_daily_spend = total_expenses / max(total_days, 1) if total_expenses > 0 else 0

        # Busiest day
        busiest_day = max(day_spending, key=day_spending.get) if day_spending else 'N/A'

        # Category percentages
        expense_percentages = {}
        if total_expenses > 0:
            for cat, amount in category_totals.items():
                expense_percentages[cat] = (amount / total_expenses) * 100
        else:
            expense_percentages = {cat: 0 for cat in category_labels}

        # ===== PREDICTIONS & FORECASTING =====
        predictions = {}
        
        # 1. Monthly expense prediction
        if len(expense_trend) >= 2:
            x_months = list(range(len(expense_trend)))
            slope, intercept = linear_regression(x_months, expense_trend)
            predicted_monthly_expense = predict_value(slope, intercept, len(expense_trend))
            if predicted_monthly_expense is None:
                predicted_monthly_expense = avg_expense * 30  # Fallback
        else:
            predicted_monthly_expense = avg_expense * 30

        # 2. Next 3 months predictions
        next_3_months_predictions = []
        if len(expense_trend) >= 2:
            x_months = list(range(len(expense_trend)))
            slope, intercept = linear_regression(x_months, expense_trend)
            for i in range(1, 4):
                pred = predict_value(slope, intercept, len(expense_trend) + i)
                next_3_months_predictions.append(max(0, pred) if pred else avg_expense * 30)
        else:
            next_3_months_predictions = [avg_expense * 30] * 3

        # 3. Yearly balance prediction
        if len(income_trend) >= 2 and len(expense_trend) >= 2:
            x_months = list(range(max(len(income_trend), len(expense_trend))))
            
            # Pad data if needed
            income_trend_padded = income_trend + [0] * (len(x_months) - len(income_trend))
            expense_trend_padded = expense_trend + [0] * (len(x_months) - len(expense_trend))
            
            income_slope, income_intercept = linear_regression(x_months, income_trend_padded)
            expense_slope, expense_intercept = linear_regression(x_months, expense_trend_padded)
            
            # Predict for next 12 months
            future_months = 12
            predicted_yearly_income = 0
            predicted_yearly_expenses = 0
            
            for i in range(len(expense_trend), len(expense_trend) + future_months):
                pred_income = predict_value(income_slope, income_intercept, i)
                pred_expense = predict_value(expense_slope, expense_intercept, i)
                predicted_yearly_income += max(0, pred_income) if pred_income else 0
                predicted_yearly_expenses += max(0, pred_expense) if pred_expense else 0
            
            predicted_yearly_balance = balance + (predicted_yearly_income - predicted_yearly_expenses)
        else:
            predicted_yearly_balance = balance + ((avg_income - avg_expense) * 12)

        # 4. Category-specific predictions (next year spending)
        category_predictions = {}
        for category in category_totals.keys():
            cat_expenses = [float(getattr(e, 'amount', 0)) for e in expenses 
                           if getattr(e, 'category', 'Other') == category]
            if cat_expenses:
                avg_cat_spending = sum(cat_expenses) / len(cat_expenses)
                yearly_prediction = avg_cat_spending * 12
                category_predictions[category] = yearly_prediction
        
        # Sort by predicted spending (descending)
        sorted_predictions = sorted(category_predictions.items(), key=lambda x: x[1], reverse=True)
        top_pred_categories = dict(sorted_predictions[:5])

        # 5. Days until balance reaches warning level (if spending continues)
        if avg_daily_spend > 0:
            days_until_low = balance / avg_daily_spend if balance > 0 else 0
        else:
            days_until_low = float('inf')

    except Exception as e:
        print(f"Error in graphs_stats: {e}")
        total_income = total_expenses = balance = 0
        category_labels = category_values = []
        top_cat_names = top_cat_values = []
        day_labels = day_values = day_transaction_counts_list = []
        month_labels = income_trend = expense_trend = []
        date_labels = date_values = []
        avg_expense = avg_income = max_expense = min_expense = 0
        avg_daily_spend = 0
        busiest_day = 'N/A'
        expense_percentages = {}
        predicted_monthly_expense = 0
        next_3_months_predictions = [0, 0, 0]
        predicted_yearly_balance = 0
        top_pred_categories = {}
        days_until_low = float('inf')

    return render_template('graphs_stats.html',
                           total_income=total_income,
                           total_expenses=total_expenses,
                           balance=balance,
                           category_labels=category_labels,
                           category_values=category_values,
                           top_cat_names=top_cat_names,
                           top_cat_values=top_cat_values,
                           day_labels=day_labels,
                           day_values=day_values,
                           day_transaction_counts=day_transaction_counts_list,
                           month_labels=month_labels,
                           income_trend=income_trend,
                           expense_trend=expense_trend,
                           date_labels=date_labels,
                           date_values=date_values,
                           avg_expense=avg_expense,
                           avg_income=avg_income,
                           max_expense=max_expense,
                           min_expense=min_expense,
                           avg_daily_spend=avg_daily_spend,
                           busiest_day=busiest_day,
                           expense_percentages=expense_percentages,
                           predicted_monthly_expense=predicted_monthly_expense,
                           next_3_months_predictions=next_3_months_predictions,
                           predicted_yearly_balance=predicted_yearly_balance,
                           top_pred_categories=top_pred_categories,
                           days_until_low=days_until_low)


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