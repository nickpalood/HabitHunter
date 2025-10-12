from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QComboBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QDateEdit, QMessageBox)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime


class ExpensesTab(QWidget):
    """Widget for managing expense entries"""

    # Common expense categories
    EXPENSE_CATEGORIES = [
        "Food & Dining",
        "Transportation",
        "Utilities",
        "Rent/Mortgage",
        "Entertainment",
        "Shopping",
        "Healthcare",
        "Education",
        "Insurance",
        "Other"
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.expense_list = []  # Will be managed by data_manager later
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()

        # Title
        title = QLabel("Expense Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Input form
        form_layout = self.create_input_form()
        layout.addLayout(form_layout)

        # Add Expense button
        add_btn = QPushButton("Add Expense")
        add_btn.clicked.connect(self.add_expense)
        add_btn.setStyleSheet("background-color: #FF5722; color: white; padding: 10px; font-weight: bold;")
        layout.addWidget(add_btn)

        # Expense table
        self.expense_table = self.create_expense_table()
        layout.addWidget(self.expense_table)

        # Delete button
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_expense)
        delete_btn.setStyleSheet("background-color: #f44336; color: white; padding: 8px;")
        layout.addWidget(delete_btn)

        self.setLayout(layout)

    def create_input_form(self):
        """Create the input form for adding expenses"""
        form = QVBoxLayout()

        # Date input
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date:"))
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        date_layout.addWidget(self.date_input)
        date_layout.addStretch()
        form.addLayout(date_layout)

        # Category dropdown
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Category:"))
        self.category_input = QComboBox()
        self.category_input.addItems(self.EXPENSE_CATEGORIES)
        category_layout.addWidget(self.category_input)
        category_layout.addStretch()
        form.addLayout(category_layout)

        # Description input
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("Description:"))
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("e.g., Grocery shopping at Walmart")
        desc_layout.addWidget(self.description_input)
        form.addLayout(desc_layout)

        # Amount input
        amount_layout = QHBoxLayout()
        amount_layout.addWidget(QLabel("Amount:"))
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0.00")
        amount_layout.addWidget(self.amount_input)
        amount_layout.addStretch()
        form.addLayout(amount_layout)

        return form

    def create_expense_table(self):
        """Create the table to display expense entries"""
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Date", "Category", "Description", "Amount"])
        table.horizontalHeader().setStretchLastSection(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        return table

    def add_expense(self):
        """Add a new expense entry"""
        # Get input values
        date = self.date_input.date().toString("yyyy-MM-dd")
        category = self.category_input.currentText()
        description = self.description_input.text().strip()
        amount_text = self.amount_input.text().strip()

        # Validate inputs
        if not description:
            QMessageBox.warning(self, "Invalid Input", "Please enter a description.")
            return

        try:
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError:
            QMessageBox.warning(self, "Invalid Amount", "Please enter a valid positive number.")
            return

        # Create expense entry
        expense_entry = {
            "date": date,
            "category": category,
            "description": description,
            "amount": amount
        }

        # Add to list and table
        self.expense_list.append(expense_entry)
        self.add_to_table(expense_entry)

        # Clear inputs
        self.clear_inputs()

        QMessageBox.information(self, "Success", "Expense added successfully!")

    def add_to_table(self, entry):
        """Add an entry to the table"""
        row = self.expense_table.rowCount()
        self.expense_table.insertRow(row)

        self.expense_table.setItem(row, 0, QTableWidgetItem(entry["date"]))
        self.expense_table.setItem(row, 1, QTableWidgetItem(entry["category"]))
        self.expense_table.setItem(row, 2, QTableWidgetItem(entry["description"]))
        self.expense_table.setItem(row, 3, QTableWidgetItem(f"${entry['amount']:.2f}"))

    def delete_expense(self):
        """Delete selected expense entry"""
        selected_row = self.expense_table.currentRow()

        if selected_row == -1:
            QMessageBox.warning(self, "No Selection", "Please select an expense entry to delete.")
            return

        reply = QMessageBox.question(self, "Confirm Delete",
                                     "Are you sure you want to delete this expense entry?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.expense_table.removeRow(selected_row)
            del self.expense_list[selected_row]
            QMessageBox.information(self, "Deleted", "Expense entry deleted successfully!")

    def clear_inputs(self):
        """Clear all input fields"""
        self.date_input.setDate(QDate.currentDate())
        self.category_input.setCurrentIndex(0)
        self.description_input.clear()
        self.amount_input.clear()

    def get_expense_data(self):
        """Return all expense data (for data_manager integration)"""
        return self.expense_list

    def load_expense_data(self, data):
        """Load expense data from data_manager"""
        self.expense_list = data
        self.expense_table.setRowCount(0)
        for entry in self.expense_list:
            self.add_to_table(entry)