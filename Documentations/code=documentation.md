# Code Documentation

This document covers the technical structure and implementation of the Simple Budget Tracker application.

## Table of Contents

- [Application Architecture](#application-architecture)
- [Route Endpoints](#route-endpoints)
- [Data Models](#data-models)
- [Helper Functions](#helper-functions)
- [Frontend Components](#frontend-components)
- [Styling System](#styling-system)

## Application Architecture

### Technology Stack

```
┌─────────────────────────────────────┐
│         Frontend (Browser)          │
│  HTML5 + CSS3 + JavaScript          │
│  Chart.js for visualizations        │
└─────────────┬───────────────────────┘
              │ HTTP Requests
┌─────────────▼───────────────────────┐
│         Flask Application           │
│  Python 3.8+ with Flask 3.0+        │
│  Jinja2 templating engine           │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│         Data Layer                  │
│  DataManager class                  │
│  In-memory storage (lists)          │
│  JSON persistence (planned)         │
└─────────────────────────────────────┘
```

### Application Flow

```
User Request
    ↓
Flask Route Handler
    ↓
Business Logic / Data Processing
    ↓
Data Manager (get/modify data)
    ↓
Template Rendering (Jinja2)
    ↓
HTML Response to Browser
    ↓
JavaScript (Charts, Form Handling)
```

## Route Endpoints

### Dashboard Routes

#### `GET /`
**Purpose**: Display main dashboard with financial overview

**Returns**: `dashboard.html`

**Context Variables**:
```python
{
    'total_income': float,              # Sum of all income
    'total_expenses': float,            # Sum of all expenses
    'balance': float,                   # income - expenses
    'income_trend': float or None,      # % change from last month
    'income_trend_direction': str,      # 'up', 'down', or 'neutral'
    'expense_trend': float or None,     # % change from last month
    'expense_trend_direction': str,     # 'up', 'down', or 'neutral'
    'recent_transactions': list,        # Last 5 transactions
    'category_labels': list,            # Category names for chart
    'category_values': list             # Amounts for chart
}
```

**Logic**:
1. Retrieve all incomes and expenses from DataManager
2. Calculate totals and balance
3. Compute current month vs last month trends
4. Get 5 most recent transactions (combined income/expenses)
5. Aggregate expenses by category for pie chart
6. Render dashboard template

---

### Income & Expense Routes

Both follow the same pattern with different data sources. Examples use `/income` but `/expenses` works identically.

#### `GET /income` or `GET /expenses`
**Purpose**: Display management page for incomes or expenses

**Returns**: `income.html` or `expenses.html`

**Context Variables**:
```python
{
    'incomes': list,              # All entries
    'total_income': float         # or total_expenses
}
```

#### `POST /income` or `POST /expenses`
**Purpose**: Add new entry

**Form Data**:
- `date` (YYYY-MM-DD)
- `category` (string)
- `amount` (positive float)
- `description` (optional)

**Validation**: All required fields present, amount positive, valid date format

#### `POST /delete_income/<id>` or `POST /delete_expense/<id>`
**Purpose**: Delete entry by index

---

### Budget Routes

#### `GET /budgets`
**Purpose**: Display budget management page

**Returns**: `budgets.html`

**Context Variables**:
```python
{
    'budgets': [
        {
            'category': str,      # Budget category
            'limit': float,       # Monthly limit
            'spent': float,       # Amount spent this month
            'remaining': float,   # limit - spent
            'percentage': float   # (spent / limit) * 100
        },
        ...
    ]
}
```

**Logic**:
1. Get all budgets from DataManager
2. Calculate spending per category from expenses
3. Compute spent, remaining, and percentage for each budget
4. Return enriched budget data

#### `POST /budgets`
**Purpose**: Create or update budget limit

**Form Data**:
- `category` (required): Expense category
- `limit` (required): Positive float for monthly limit

**Validation**:
1. Category and limit provided
2. Limit is positive number

**Logic**:
1. Check if budget exists for category
2. If exists: update limit
3. If new: create new budget
4. Save to DataManager

**Response**: Redirect to `/budgets` with flash message

---

#### `POST /delete_budget/<int:budget_id>`
**Purpose**: Delete budget by index

**Parameters**:
- `budget_id`: Index in budgets list

**Response**: Redirect to `/budgets` with success/error message

---

### Report Routes

#### `GET /reports`
**Purpose**: Display financial reports with charts

**Returns**: `reports.html`

**Context Variables**:
```python
{
    'total_income': float,
    'total_expenses': float,
    'balance': float,
    'expense_by_category': [        # Detailed category breakdown
        {
            'category': str,
            'amount': float,
            'percentage': float
        },
        ...
    ],
    'category_labels': list,        # For pie chart
    'category_values': list,        # For pie chart
    'monthly_data': bool,           # True if enough data for trends
    'month_labels': list,           # e.g., ['Nov 2025', 'Dec 2025']
    'income_trend': list,           # Monthly income amounts
    'expense_trend': list,          # Monthly expense amounts
    'recent_transactions': list     # Last 10 transactions
}
```

**Logic**:
1. Aggregate expenses by category
2. Group income/expenses by month (YYYY-MM format)
3. Sort months chronologically
4. Build trend data arrays
5. Get last 10 transactions sorted by date

---

### Analytics Routes

#### `GET /graphs-stats`
**Purpose**: Advanced analytics with predictions

**Returns**: `graphs_stats.html`

**Context Variables** (extensive):
```python
{
    # Basic stats
    'total_income': float,
    'total_expenses': float,
    'balance': float,
    
    # Category analysis
    'category_labels': list,
    'category_values': list,
    'top_cat_names': list,          # Top 5 categories
    'top_cat_values': list,
    
    # Day of week analysis
    'day_labels': list,             # ['Monday', 'Tuesday', ...]
    'day_values': list,             # Spending per day
    'day_transaction_counts': list, # Transactions per day
    
    # Monthly trends
    'month_labels': list,
    'income_trend': list,
    'expense_trend': list,
    
    # Daily spending
    'date_labels': list,            # Specific dates
    'date_values': list,            # Spending on each date
    
    # Statistics
    'avg_expense': float,
    'avg_income': float,
    'max_expense': float,
    'min_expense': float,
    'avg_daily_spend': float,
    'busiest_day': str,             # Day name with most spending
    'expense_percentages': dict,    # Category → percentage
    
    # Predictions (using linear regression)
    'predicted_monthly_expense': float,
    'next_3_months_predictions': list,      # [month1, month2, month3]
    'predicted_yearly_balance': float,
    'top_pred_categories': dict,            # Top 5 predicted categories
    'days_until_low': float                 # Days until balance runs out
}
```

**Logic**: (Most complex route)
1. Calculate all basic statistics
2. Aggregate spending by day of week
3. Build comprehensive monthly trends
4. Perform linear regression on historical data
5. Generate predictions for future spending
6. Calculate category-specific forecasts

---

### Utility Routes

#### `GET /save`
**Purpose**: Trigger data save to file

**Logic**: Calls `data_manager.save()` (currently placeholder - no file I/O implemented yet)

**Response**: Redirect to dashboard with message

---

## Data Models

### Income Entry

```python
{
    'date': str,          # Format: 'YYYY-MM-DD'
    'category': str,      # One of 10 predefined categories
    'amount': float,      # Positive number
    'description': str    # Optional user note
}
```

**Stored as**: `type('Income', (), dict)` - Dynamic object creation

### Expense Entry

```python
{
    'date': str,          # Format: 'YYYY-MM-DD'
    'category': str,      # One of 10 predefined categories
    'amount': float,      # Positive number
    'description': str    # Optional user note
}
```

**Stored as**: `type('Expense', (), dict)` - Dynamic object creation

### Budget Entry

```python
{
    'category': str,      # Expense category to budget
    'limit': float        # Monthly spending limit
}
```

**Stored as**: `type('Budget', (), dict)` - Dynamic object creation

---

## Helper Functions

### `linear_regression(x_values, y_values)`

**Purpose**: Perform simple linear regression using least squares method

**Parameters**:
- `x_values` (list): Independent variable (e.g., [0, 1, 2, 3])
- `y_values` (list): Dependent variable (e.g., [100, 150, 180, 220])

**Returns**: `(slope, intercept)` tuple or `(None, None)` if insufficient data

**Algorithm**:
```
slope = Σ((x - x̄)(y - ȳ)) / Σ((x - x̄)²)
intercept = ȳ - slope * x̄

where:
x̄ = mean of x values
ȳ = mean of y values
```

**Usage Example**:
```python
months = [0, 1, 2, 3]      # Month indices
spending = [500, 550, 600, 650]  # Monthly spending

slope, intercept = linear_regression(months, spending)
# slope ≈ 50 (spending increases $50/month)
# intercept ≈ 500 (starting point)
```

---

### `predict_value(slope, intercept, x)`

**Purpose**: Predict future value using linear regression coefficients

**Parameters**:
- `slope` (float): Regression slope
- `intercept` (float): Regression intercept
- `x` (float): Input value to predict for

**Returns**: `float` - Predicted value, or `None` if coefficients are None

**Formula**: `y = slope * x + intercept`

**Usage Example**:
```python
# Predict spending for month 4
next_month = predict_value(slope, intercept, 4)
# Returns approximately 700
```

---

## Frontend Components

### HTML Structure

All templates use a consistent structure: navbar with brand/navigation, main container with page header, flash messages for feedback, page content, and optional JavaScript for charts/forms. See the styling system section below for component classes and styling details.

### Jinja2 Template Syntax

Key patterns used throughout:
- **Variables**: `{{ variable_name }}`, `{{ obj.property }}`, `{{ value|format('%.2f') }}`
- **Conditionals**: `{% if condition %} ... {% else %} ... {% endif %}`
- **Loops**: `{% for item in items %} ... {% endfor %}`
- **Flask integration**: `{{ url_for('route_name') }}`, `{{ get_flashed_messages() }}`

---

### Chart.js Integration

Two main chart types are used:
- **Pie/Doughnut charts** for category breakdowns: Pass `labels` and `values` via Jinja's `tojson` filter
- **Line charts** for trends: Multiple datasets (Income/Expenses) with month labels on x-axis

Both use responsive options and custom color scheme from the CSS variables (see Styling System). The template converts Python lists to JSON using `{{ data|tojson }}`.

---

## Styling System

### CSS Variables (from base.css)

```css
:root {
    /* Primary colors */
    --primary: #a855f7;         /* Purple */
    --primary-dark: #9333ea;
    --primary-light: #e9d5ff;
    
    /* Status colors */
    --success: #10b981;         /* Green */
    --success-light: #d1fae5;
    --danger: #ef4444;          /* Red */
    --danger-light: #fee2e2;
    --warning: #f59e0b;         /* Orange */
    --accent: #06b6d4;          /* Cyan */
    
    /* Gray scale */
    --gray-50: #fafafa;
    --gray-100: #f3f4f6;
    --gray-200: #e5e7eb;
    --gray-300: #d1d5db;
    --gray-400: #9ca3af;
    --gray-500: #6b7280;
    --gray-600: #4b5563;
    --gray-700: #374151;
    --gray-800: #1f2937;
    --gray-900: #111827;
    
    /* Shadows */
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}
```

### Component Classes

**Cards**:
```css
.card              /* White background, rounded, shadow */
.stat-card         /* Stats with colored accents */
.stat-card.income  /* Green accent */
.stat-card.expense /* Red accent */
.stat-card.balance /* Purple accent */
```

**Buttons**:
```css
.btn               /* Primary purple button */
.btn-secondary     /* Gray button */
.btn-danger        /* Red delete button */
.btn-small         /* Smaller button */
```

**Forms**:
```css
.form-row          /* Grid layout for form fields */
.form-group        /* Individual form field wrapper */
label              /* Bold, dark labels */
input, select      /* Styled inputs with focus states */
```

**Transactions**:
```css
.transaction-item          /* Container for transaction */
.transaction-icon          /* Colored icon circle */
.transaction-icon.income   /* Green gradient */
.transaction-icon.expense  /* Red gradient */
.transaction-details       /* Transaction text info */
.transaction-amount        /* Amount display */
.transaction-amount.positive  /* Green + amount */
.transaction-amount.negative  /* Red - amount */
```

**Tables**:
```css
.table-container   /* Scrollable table wrapper */
thead              /* Table header with gray background */
tbody tr:hover     /* Row hover effect */
```

**Utilities**:
```css
.positive          /* Green text color */
.negative          /* Red text color */
.text-muted        /* Gray text */
.empty-state       /* Empty state placeholder */
```

---

## Data Flow Examples

### Adding an Expense

```
1. User fills form on /expenses page
   ↓
2. Form submits POST to /expenses
   ↓
3. Flask route handler receives form data
   ↓
4. Validation:
   - Check all required fields present
   - Verify amount is positive float
   ↓
5. Create expense dictionary:
   {date, category, amount, description}
   ↓
6. Convert to dynamic object:
   type('Expense', (), expense_dict)
   ↓
7. Append to data_manager._expenses list
   ↓
8. Flash success message
   ↓
9. Redirect back to /expenses
   ↓
10. GET /expenses renders updated list
    ↓
11. Template displays all expenses including new one
```

### Generating Reports

```
1. User clicks "Reports" in navbar
   ↓
2. GET /reports route triggered
   ↓
3. Retrieve incomes and expenses from DataManager
   ↓
4. Calculate totals and balance
   ↓
5. Aggregate expenses by category:
   defaultdict(float)
   for each expense:
       category_totals[expense.category] += expense.amount
   ↓
6. Group by month:
   for each transaction:
       parse date -> extract YYYY-MM
       accumulate amounts per month
   ↓
7. Sort months chronologically:
   sorted(all_month_keys)  # Uses YYYY-MM format
   ↓
8. Build chart data arrays:
   month_labels = []
   income_trend = []
   expense_trend = []
   ↓
9. Render template with all data
   ↓
10. JavaScript creates Chart.js visualizations
```

---

## Code Examples

### Creating a New Route

```python
@app.route('/my-feature', methods=['GET', 'POST'])
def my_feature():
    """
    Description of what this route does.
    
    GET: Display the feature page
    POST: Process form submission
    """
    if request.method == 'POST':
        # Handle form submission
        data = request.form.get('data')
        
        # Validate
        if not data:
            flash('Data is required!')
            return redirect(url_for('my_feature'))
        
        # Process data
        result = process_data(data)
        
        # Store in data manager
        data_manager.add_item(result)
        
        flash('Success!')
        return redirect(url_for('my_feature'))
    
    # GET request
    items = data_manager.get_items()
    return render_template('my_feature.html', items=items)
```

### Accessing Form Data

```python
# Single value
value = request.form.get('field_name')

# With default
value = request.form.get('field_name', 'default_value')

# Multiple values (checkboxes)
values = request.form.getlist('field_name')
```

### Working with DataManager

```python
# Get data
incomes = data_manager.get_incomes()
expenses = data_manager.get_expenses()
budgets = data_manager.get_budgets()

# Add new entry
new_income = type('Income', (), {
    'date': '2025-12-08',
    'category': 'Salary',
    'amount': 3000.0,
    'description': 'Monthly salary'
})
data_manager._incomes.append(new_income)

# Delete entry
del data_manager._expenses[0]  # Delete first expense

# Iterate
for income in data_manager.get_incomes():
    date = getattr(income, 'date', '')
    amount = float(getattr(income, 'amount', 0))
    print(f"{date}: ${amount}")
```

---

## Troubleshooting

### Charts Not Showing Up

If the charts aren't rendering, the most common cause is that the Chart.js library isn't actually loaded. We've encountered this more times than we'd like to admit. Make sure the CDN script tag is in the template head, and check your browser console for any JavaScript errors. Also double-check that the data passed to Chart.js is properly formatted as JSON using the `tojson` filter.

### Template Changes Not Appearing

Browser caching usually causes this. Do a hard refresh (Ctrl+Shift+R on Windows, Cmd+Shift+R on Mac) to force reload without cache. When actively developing, we sometimes add a version parameter to the CSS link as a cache buster so we don't have to keep doing hard refreshes.

### Dynamic Object Attributes Returning Wrong Values

The dynamic objects created with `type()` can be finicky. We always use `getattr()` with a default value instead of directly accessing attributes. They don't behave exactly like regular class instances, so checking if an attribute exists first saves a lot of debugging headache.

---

For more details, check out the DEVELOPER_GUIDE or ask around if you get stuck.

