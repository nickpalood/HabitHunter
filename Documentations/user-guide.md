# User Guide

Welcome to Simple Budget Tracker. This guide explains how to use the application.

## Table of Contents

- Getting Started
- Dashboard Overview
- Managing Income
- Tracking Expenses
- Setting Budgets
- Viewing Reports
- Advanced Analytics
- Tips & Best Practices
- FAQ

## Getting Started

### First time using the app

1. Open your web browser and go to http://localhost:5000
2. You'll land on the dashboard - this is your main view
3. The navigation bar at the top lets you move between different sections

### Main Sections

- **Dashboard**: Quick overview of everything
- **Income**: Add money you've received
- **Expenses**: Track what you've spent
- **Budgets**: Set spending limits for different categories
- **Reports**: See charts and breakdowns of your finances
- **Graphs & Stats**: More detailed analysis and predictions

## Dashboard

This is where you'll probably spend most of your time. Here's what you'll see:

**Balance Card** - Shows how much money you have left (total income minus total expenses)

**Quick Actions** - Buttons to quickly add income, expenses, view budgets, etc.

**Quick Stats** - Your total income and expenses at a glance

**Spending Breakdown** - A pie chart showing where your money goes

**Recent Transactions** - Your last 5 transactions so you can see recent activity

## Adding Income

Go to the Income page and fill out the form:

- **Date**: When you got the money (defaults to today)
- **Category**: Pick what type of income it is
  - Salary, Freelance, Business, Investment Returns, Rental Income, Side Hustle, Gift/Bonus, Refund, Interest, or Other
- **Amount**: How much you received
- **Description**: Optional notes like "November paycheck" or "Sold old textbooks"

Click "Add Income" and it'll show up in your list below. The green card at the top shows your total income.

To delete an entry, just click the red Delete button next to it.

## Tracking Expenses

Go to the Expenses page and fill out the form:

- **Date**: When you spent the money
- **Category**: What type of expense
  - Food & Dining, Transportation, Utilities, Rent/Mortgage, Entertainment, Shopping, Healthcare, Education, Insurance, or Other
- **Amount**: How much you spent
- **Description**: Optional details like "Groceries" or "New headphones"

Your expenses show up in red with a minus sign. The card at the top shows your total spending.

## Setting Budgets

Budgets help you avoid overspending. Go to the Budgets page and create one:

- **Category**: Which expense category you want to budget for
- **Monthly Limit**: How much you want to spend max per month

Once you create a budget, you'll see a progress bar showing how much you've spent vs. your limit:

- **Green**: You're doing fine (under 80% of your limit)
- **Yellow**: Getting close (80-99% used)
- **Red**: You've gone over budget

If you want to change a budget, delete the old one and make a new one with the updated amount.

## Reports Page

This is where you can see your financial overview.

**Overview Stats** - Three cards showing total income, expenses, and net balance

**Spending Breakdown** - Pie chart and table showing which categories you spend the most on

**Monthly Trend** - Line chart showing your income and expenses over time. Useful for spotting patterns.

**Transaction History** - Table of your last 10 transactions



## Graphs & Stats

This page provides more detailed analysis:

**Statistics** - Average daily spending, biggest single expense, which day of the week you spend the most, etc.

**Charts** - Spending by day of week, daily timeline, and top 5 spending categories

**Predictions** - The app predicts future spending based on your history. These are estimates based on current trends and need at least a couple months of data to be reliable.

### Using the Application

- Add transactions as soon as possible while you remember what they were for
- Be consistent with categories across all entries
- Check your stats weekly to catch problems early
- If you see a warning on a budget, reduce spending in that category

### Setting Good Budgets

Start with the big expenses: rent, food, transportation. Look at what you actually spent last month and set limits based on reality. Add a buffer for unexpected costs.

## Category Guide

Quick reference for where to categorize different transactions:

- **Food & Dining**: Groceries, restaurants, coffee, food delivery
- **Transportation**: Gas, public transit, parking, Uber
- **Utilities**: Electricity, water, internet, phone
- **Entertainment**: Movies, concerts, streaming services, hobbies
- **Shopping**: Clothes, electronics, random stuff, gifts
- **Healthcare**: Doctor visits, prescriptions, health insurance
- **Education**: Textbooks, courses, school supplies
- **Insurance**: Car, home, life insurance (not health)
- **Other**: Anything that doesn't fit elsewhere

## FAQ

**Where is my data stored?**

Currently all data is stored in memory only, which means it will be cleared when you close the application.

**Can I recover deleted transactions?**

No, deleted transactions are gone permanently. Be careful with the delete button.

**Why aren't my charts showing?**

Charts require an internet connection since they load from a CDN. Try refreshing the page if they don't appear.

**Can I add my own categories?**

Not currently - you're limited to the preset categories for income and expenses. The app provides the most common financial categories. Use "Other" for anything that doesn't fit.


*Is my data secure?*
Yeah, everything stays on your computer. Nothing gets sent anywhere.

If something breaks

Try refreshing the page first. If that doesn't work, clear your browser cache or try a different browser. If you find a bug, let the dev team know what you were doing when it happened.

---

That's pretty much it. Start adding your transactions, set some budgets, and check the reports regularly. You'll get the hang of it pretty quickly.