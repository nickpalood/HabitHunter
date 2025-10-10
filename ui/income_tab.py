from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QComboBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QDateEdit, QMessageBox)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime

#introducing the income tab class
class IncomeTab(QWidget):
    """Widget for managing income entries"""

    # Common income categories
    INCOME_CATEGORIES = [
        "Salary",
        "Freelance",
        "Business",
        "Investment Returns",
        "Rental Income",
        "Side Hustle",
        "Gift/Bonus",
        "Refund",
        "Interest",
        "Other"
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.income_list = []  # Will be managed by data_manager later
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()

        # Title
        title = QLabel("Income Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Input form
        form_layout = self.create_input_form()
        layout.addLayout(form_layout)

        # Add Income button
        add_btn = QPushButton("Add Income")
        add_btn.clicked.connect(self.add_income)
        add_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-weight: bold;")
        layout.addWidget(add_btn)

        # Income table
        self.income_table = self.create_income_table()
        layout.addWidget(self.income_table)

        # Delete button
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_income)
        delete_btn.setStyleSheet("background-color: #f44336; color: white; padding: 8px;")
        layout.addWidget(delete_btn)

        self.setLayout(layout)

    def create_input_form(self):
        """Create the input form for adding income"""
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
        self.category_input.addItems(self.INCOME_CATEGORIES)
        category_layout.addWidget(self.category_input)
        category_layout.addStretch()
        form.addLayout(category_layout)

        # Description input
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("Description:"))
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("e.g., Monthly salary payment")
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

    def create_income_table(self):
        """Create the table to display income entries"""
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Date", "Category", "Description", "Amount"])
        table.horizontalHeader().setStretchLastSection(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        return table

    def add_income(self):
        """Add a new income entry"""
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

        # Create income entry
        income_entry = {
            "date": date,
            "category": category,
            "description": description,
            "amount": amount
        }

        # Add to list and table
        self.income_list.append(income_entry)
        self.add_to_table(income_entry)

        # Clear inputs
        self.clear_inputs()

        QMessageBox.information(self, "Success", "Income added successfully!")

    def add_to_table(self, entry):
        """Add an entry to the table"""
        row = self.income_table.rowCount()
        self.income_table.insertRow(row)

        self.income_table.setItem(row, 0, QTableWidgetItem(entry["date"]))
        self.income_table.setItem(row, 1, QTableWidgetItem(entry["category"]))
        self.income_table.setItem(row, 2, QTableWidgetItem(entry["description"]))
        self.income_table.setItem(row, 3, QTableWidgetItem(f"${entry['amount']:.2f}"))

    def delete_income(self):
        """Delete selected income entry"""
        selected_row = self.income_table.currentRow()

        if selected_row == -1:
            QMessageBox.warning(self, "No Selection", "Please select an income entry to delete.")
            return

        reply = QMessageBox.question(self, "Confirm Delete",
                                     "Are you sure you want to delete this income entry?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.income_table.removeRow(selected_row)
            del self.income_list[selected_row]
            QMessageBox.information(self, "Deleted", "Income entry deleted successfully!")

    def clear_inputs(self):
        """Clear all input fields"""
        self.date_input.setDate(QDate.currentDate())
        self.category_input.setCurrentIndex(0)
        self.description_input.clear()
        self.amount_input.clear()

    def get_income_data(self):
        """Return all income data (for data_manager integration)"""
        return self.income_list

    def load_income_data(self, data):
        """Load income data from data_manager"""
        self.income_list = data
        self.income_table.setRowCount(0)
        for entry in self.income_list:
            self.add_to_table(entry)