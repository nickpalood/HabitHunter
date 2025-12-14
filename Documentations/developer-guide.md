# Developer Guide

This is the guide for everyone working on the Simple Budget Tracker project.

## Table of Contents
- [Getting Started](#getting-started)
- [Code Structure](#code-structure)
- [Adding New Features](#adding-new-features)
- [Coding Standards](#coding-standards)
- [Git Workflow](#git-workflow)
- [Testing](#testing)

## Getting Started

### Development Environment Setup

1. **Clone the repository** (requires university git.liacs credentials)
   ```bash
   # This is a private school project on git.liacs.leidenuniv.nl
   git clone https://git.liacs.leidenuniv.nl/simple-budget-tracker.git
   cd simple-budget-tracker
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask
   ```

4. **Run in development mode**
   ```bash
   python app.py
   ```
   The app runs on `http://localhost:5000` (default Flask port) with debug mode enabled.

### IDE Recommendations
- **PyCharm** - Full-featured Python IDE
- **VS Code** - Lightweight with Python extensions
- **Sublime Text** - Fast and simple

## Code Structure

### app.py - Main Application File

The `app.py` file contains all Flask routes and application logic:

#### Key Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Dashboard with overview |
| `/income` | GET, POST | Income management |
| `/expenses` | GET, POST | Expense tracking |
| `/budgets` | GET, POST | Budget limits |
| `/reports` | GET | Financial reports |
| `/graphs-stats` | GET | Advanced analytics and predictions |
| `/delete_income/<id>` | POST | Delete income entry |
| `/delete_expense/<id>` | POST | Delete expense entry |
| `/delete_budget/<id>` | POST | Delete budget |


### models/data_manager.py

```python
class DataManager:
    def __init__(self, path: str):
        self.path = path
        self._incomes = []    # List of income entries
        self._expenses = []   # List of expense entries
        self._budgets = []    # List of budget limits
    
    def get_incomes(self):
        return self._incomes
    
    def get_expenses(self):
        return self._expenses
    
    def get_budgets(self):
        return self._budgets
    
    def load(self):
        # TODO: Implement JSON file loading
        pass
    
    def save(self):
        # TODO: Implement JSON file saving
        pass
```

**Current State**: In-memory storage only
**Future Enhancement**: Full JSON persistence

### Template Structure

All HTML templates inherit from a base structure with:
- **Navbar**: Consistent navigation across pages
- **Container**: Main content area
- **Flash messages**: User feedback
- **Cards**: Content organization

### CSS Architecture

**base.css** - Shared styles for all pages
- CSS variables for colors and spacing
- Navbar styling
- Card and component styling
- Form elements
- Button styles
- Table styling
- Responsive design with breakpoints

**Note**: Page-specific CSS files (dashboard.css, income.css, etc.) exist but are not currently used. All styling is consolidated in base.css.

## Adding New Features

### Adding a New Page

1. **Create the route in app.py**
   ```python
   @app.route('/my-feature')
   def my_feature():
       # Your logic here
       data = process_data()
       return render_template('my_feature.html', data=data)
   ```

2. **Create the HTML template**
   ```html
   <!DOCTYPE html>
   <html lang="en">
   <head>
       <meta charset="UTF-8">
       <title>My Feature - Simple Budget Tracker</title>
       <link rel="stylesheet" href="{{ url_for('static', filename='base.css') }}">
   </head>
   <body>
       <!-- Copy navbar from another template -->
       <div class="navbar">...</div>
       
       <div class="container container-lg">
           <h1>My Feature</h1>
           <!-- Your content -->
       </div>
   </body>
   </html>
   ```

3. **Add navigation link**
   Update the navbar in all templates:
   ```html
   <a href="{{ url_for('my_feature') }}">My Feature</a>
   ```

### Adding a New Income/Expense Category

1. **Update the HTML template**
   In `templates/income.html` or `templates/expenses.html`:
   ```html
   <option value="New Category">New Category</option>
   ```

2. **No backend changes needed** - Categories are stored as strings

### Adding Chart Visualizations

1. **Prepare data in the route**
   ```python
   @app.route('/my-chart')
   def my_chart():
       labels = ['Jan', 'Feb', 'Mar']
       values = [100, 200, 150]
       return render_template('chart.html', 
                            labels=labels, 
                            values=values)
   ```

2. **Add Chart.js in the template**
   ```html
   <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
   <canvas id="myChart"></canvas>
   
   <script>
   new Chart(document.getElementById('myChart'), {
       type: 'bar',
       data: {
           labels: {{ labels|tojson }},
           datasets: [{
               data: {{ values|tojson }},
               backgroundColor: '#a855f7'
           }]
       }
   });
   </script>
   ```

## Coding Standards

### Python Style Guide

Follow PEP 8 guidelines:

```python
# Good: Clear function name, docstring, type hints
def calculate_total_expenses(expenses: list) -> float:
    """
    Calculate the sum of all expense amounts.
    
    Args:
        expenses: List of expense objects
        
    Returns:
        Total sum of expenses as float
    """
    return sum([float(getattr(e, 'amount', 0)) for e in expenses])

# Bad: No documentation, unclear name
def calc(e):
    return sum([float(getattr(x, 'amount', 0)) for x in e])
```

### HTML/CSS Standards

- Use semantic HTML5 elements
- Keep inline styles minimal (use CSS classes)
- Follow the existing naming conventions:
  - Cards: `.card`
  - Buttons: `.btn`, `.btn-primary`, `.btn-danger`
  - Forms: `.form-group`, `.form-row`

### JavaScript Standards

- Use modern ES6+ syntax
- Keep scripts at the bottom of the page
- Use `const` and `let`, avoid `var`
- Comment complex logic

```javascript
// Good: Clear, documented
const categoryChart = document.getElementById('categoryChart');
new Chart(categoryChart, {
    type: 'doughnut',
    data: chartData,
    options: chartOptions
});

// Bad: Unclear variable names
var c = document.getElementById('c');
new Chart(c, {type: 'd', data: d});
```

### Git Commit Messages

Format: `[Component] Brief description`

Examples:
- `[Income] Add description field to income entries`
- `[Dashboard] Fix balance calculation bug`
- `[Reports] Improve chart colors and layout`
- `[Docs] Update README with installation steps`

## Git Workflow

### Branch Strategy

```
main (or master)
  ├── dev
  │   ├── feature/income-expenses-tabs
  │   ├── feature/budget-management
  │   ├── feature/reports-dashboard
  │   └── feature/data-persistence
```

### Creating a Feature Branch

```bash
# Make sure you're on main/dev
git checkout main
git pull origin main

# Create your feature branch
git checkout -b feature/my-feature-name
```

### Making Changes

```bash
# Check what changed
git status

# Add your changes
git add file1.py file2.html

# Commit with a clear message
git commit -m "[Feature] Add new analytics chart"

# Push to your branch
git push origin feature/my-feature-name
```

### Creating a Pull Request

1. Push your branch to git.liacs
2. Go to the repository on git.liacs.leidenuniv.nl
3. Click "Merge Request" or "Compare & Pull Request"
4. **Target branch**: `dev` (not `main`!)
5. Add a description of your changes
6. Request reviews from teammates
7. Wait for approval and merge

### Handling Merge Conflicts

```bash
# Update your branch with latest dev
git checkout dev
git pull origin dev
git checkout feature/my-feature
git merge dev

# If conflicts occur, edit the files manually
# Then:
git add resolved-file.py
git commit -m "Resolve merge conflict"
git push origin feature/my-feature
```

## Testing

### Manual Testing Checklist

Before committing, test:

- [ ] Income page: Add, view, delete entries
- [ ] Expenses page: Add, view, delete entries
- [ ] Budgets page: Create, monitor, delete budgets
- [ ] Reports page: Charts display correctly
- [ ] Dashboard: Balance and recent transactions update
- [ ] All navigation links work
- [ ] Forms validate input correctly
- [ ] Responsive design works on mobile (use browser dev tools)

### Testing with Sample Data

```python
# In Python console or temporary test file
from models.data_manager import DataManager

dm = DataManager('data/budget_data.json')

# Add test income
dm._incomes.append(type('Income', (), {
    'date': '2024-12-01',
    'category': 'Salary',
    'amount': 3000.0
}))

# Add test expense
dm._expenses.append(type('Expense', (), {
    'date': '2024-12-05',
    'category': 'Food & Dining',
    'amount': 50.0
}))

print(f"Incomes: {len(dm.get_incomes())}")
print(f"Expenses: {len(dm.get_expenses())}")
```

### Browser Testing

Test in multiple browsers:
- Chrome/Edge (Chromium)
- Firefox
- Safari (if on Mac)

### Mobile Testing

1. Open browser dev tools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Test different screen sizes:
   - Mobile: 375px width
   - Tablet: 768px width
   - Desktop: 1280px width

## Debugging Tips

### Flask Debug Mode

Debug mode is enabled by default:
```python
app.run(debug=True, port=5000)
```

This provides:
- Automatic reloading when files change
- Detailed error messages in browser
- Interactive debugger

### Print Debugging

```python
@app.route('/expenses', methods=['POST'])
def expenses():
    date = request.form.get('date')
    amount = request.form.get('amount')
    
    print(f"DEBUG: Received expense - Date: {date}, Amount: {amount}")
    
    # Rest of the code...
```

### Common Issues

**Problem**: Charts not displaying
- **Solution**: Check browser console for JavaScript errors
- Verify Chart.js CDN is loaded
- Ensure data is properly formatted as JSON

**Problem**: Styles not applying
- **Solution**: Hard refresh browser (Ctrl+Shift+R)
- Check if CSS file is linked correctly
- Verify CSS class names match

**Problem**: Form submission not working
- **Solution**: Check form `method="POST"` and `action` attributes
- Verify all required fields have `name` attributes
- Check Flask route accepts POST method

## Dependencies

Current dependencies (in `requirements.txt`):
```
Flask>=3.0.0
```

Flask automatically installs required dependencies (Werkzeug, Jinja2, etc.).

To generate automatically:
```bash
pip freeze > requirements.txt
```

To install from requirements:
```bash
pip install -r requirements.txt
```

## Learning Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Jinja2 Templates](https://jinja.palletsprojects.com/)
- [Chart.js Documentation](https://www.chartjs.org/docs/)
- [MDN Web Docs](https://developer.mozilla.org/) - HTML/CSS/JS reference

## Tips for Success

1. Commit often - small, frequent commits are better than large ones
2. Test before pushing - always test your changes locally
3. Ask for help - don't struggle alone, reach out to the team
4. Document as you go - update docs when adding features
5. Review each other's code - learn from your teammates' pull requests

---

