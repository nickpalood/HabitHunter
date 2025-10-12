from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QMessageBox, QStatusBar
)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime

# --- flexible imports: works when run as a script OR as a module ---
try:
    # When run as a module:  python -m ui.main_window
    from .dashboard_tab import DashboardTab
    from .income_tab import IncomeTab
    from .expenses_tab import ExpensesTab
    from .budget_tab import BudgetTab
    from .reports_tab import ReportsTab
except ImportError:
    # When run directly: python ui/main_window.py
    from dashboard_tab import DashboardTab
    from income_tab import IncomeTab
    from expenses_tab import ExpensesTab
    from budget_tab import BudgetTab
    from reports_tab import ReportsTab

# models import (needs project root on sys.path when run directly)
try:
    from models.data_manager import DataManager
except ModuleNotFoundError:
    import os, sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from models.data_manager import DataManager



class MainWindow(QMainWindow):
    """
    Main application window that hosts all tabs and coordinates data loading/saving.
    Keeps dependencies light: the tabs are responsible for their own UI and expose
    optional .refresh() methods and optional .changed signals when their data mutates.
    """
    def __init__(self, data_path: str = "data/budget_data.json", parent=None):
        super().__init__(parent)

        # --- Core state ---
        self.data_manager = DataManager(data_path)
        self.setWindowTitle("Budget Tracker")
        self.resize(1100, 720)

        # Load data (non-fatal if first run / empty file)
        load_ok, load_err = self._safe_load()
        if not load_ok and load_err:
            QMessageBox.warning(
                self,
                "Load Warning",
                f"Couldn't load existing data from:\n{data_path}\n\n"
                f"Reason: {load_err}\n\nA new file will be created on save."
            )

        # --- Central widget & layout scaffolding ---
        central = QWidget(self)
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(10)

        # Header bar
        self.header_bar = self._build_header_bar()
        outer.addLayout(self.header_bar)

        # Tabs
        self.tabs = QTabWidget(self)
        self.tabs.setDocumentMode(True)
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        outer.addWidget(self.tabs, 1)

        # Status bar
        self.status = QStatusBar(self)
        self.setStatusBar(self.status)

        # Instantiate and add tabs
        self._init_tabs()

        # Initial refresh of all tabs
        self.refresh_all_tabs()

        # Show a quick status hint
        self._set_status("Ready")

    # -------------------------------------------------------------------------
    # UI construction helpers
    # -------------------------------------------------------------------------
    def _build_header_bar(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(10)

        self.title_label = QLabel("💰 Budget Tracker")
        self.title_label.setStyleSheet("font-weight: 600; font-size: 18px;")
        layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignVCenter)

        layout.addStretch(1)

        self.summary_label = QLabel("")
        self.summary_label.setToolTip("Quick summary based on current data")
        layout.addWidget(self.summary_label, alignment=Qt.AlignmentFlag.AlignVCenter)

        layout.addStretch(1)

        self.last_saved_label = QLabel("Last saved: —")
        self.last_saved_label.setObjectName("lastSavedLabel")
        layout.addWidget(self.last_saved_label, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self.refresh_all_tabs)
        layout.addWidget(self.btn_refresh)

        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self.save_data)
        layout.addWidget(self.btn_save)

        return layout

    def _init_tabs(self) -> None:
        """
        Create each tab, give them access to the shared DataManager,
        and (optionally) wire up their change signals back to us.
        """
        self.dashboard_tab = DashboardTab(self.data_manager, parent=self)
        self.income_tab = IncomeTab(self.data_manager, parent=self)
        self.expenses_tab = ExpensesTab(self.data_manager, parent=self)
        self.budget_tab = BudgetTab(self.data_manager, parent=self)
        self.reports_tab = ReportsTab(self.data_manager, parent=self)

        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        self.tabs.addTab(self.income_tab, "Income")
        self.tabs.addTab(self.expenses_tab, "Expenses")
        self.tabs.addTab(self.budget_tab, "Budgets")
        self.tabs.addTab(self.reports_tab, "Reports")

        # If tabs expose a `changed` signal, connect it to keep everything in sync
        for tab in (self.dashboard_tab, self.income_tab, self.expenses_tab, self.budget_tab, self.reports_tab):
            sig = getattr(tab, "changed", None)
            if sig is not None:
                try:
                    sig.connect(self._on_tab_changed)
                except Exception:
                    # Not a Qt signal or failed to connect — ignore silently
                    pass

    # -------------------------------------------------------------------------
    # Data operations
    # -------------------------------------------------------------------------
    def _safe_load(self) -> tuple[bool, str | None]:
        try:
            self.data_manager.load()
            return True, None
        except Exception as e:
            return False, str(e)

    def save_data(self) -> None:
        try:
            self.data_manager.save()
            self._touch_last_saved()
            self._set_status("Data saved.")
            QMessageBox.information(self, "Saved", "Your budget data has been saved.")
        except Exception as e:
            self._set_status("Save failed.")
            QMessageBox.critical(
                self,
                "Save Error",
                f"Couldn't save your data.\n\nReason: {e}"
            )

    # -------------------------------------------------------------------------
    # Refresh & synchronization
    # -------------------------------------------------------------------------
    def refresh_all_tabs(self) -> None:
        """
        Ask each tab to re-render itself. Tabs may implement .refresh().
        """
        for tab in (self.dashboard_tab, self.income_tab, self.expenses_tab, self.budget_tab, self.reports_tab):
            refresher = getattr(tab, "refresh", None)
            if callable(refresher):
                try:
                    refresher()
                except Exception:
                    # A tab failed to refresh; keep the rest going
                    pass

        # Also refresh the header summary after tabs update (so totals are current)
        self._update_header_summary()

    def _on_tab_changed(self) -> None:
        """
        Called when any tab signals that underlying data changed.
        We refresh everyone to keep a single source of truth (DataManager).
        """
        self.refresh_all_tabs()
        # Light autosave strategy (optional): comment out if undesired.
        try:
            self.data_manager.save()
            self._touch_last_saved()
            self._set_status("Changes auto-saved.")
        except Exception:
            self._set_status("Changes captured (autosave failed).")

    # -------------------------------------------------------------------------
    # Header helpers
    # -------------------------------------------------------------------------
    def _update_header_summary(self) -> None:
        """
        Compute and display a quick, human-readable summary in the header.
        Assumes DataManager exposes aggregate helpers; falls back gracefully if not.
        """
        try:
            # Prefer dedicated helpers if your DataManager provides them:
            # total_income = self.data_manager.total_income()
            # total_expenses = self.data_manager.total_expenses()
            # balance = total_income - total_expenses
            #
            # If not available, fall back to raw data access patterns that your
            # DataManager likely supports (adjust names if needed):
            total_income = 0.0
            total_expenses = 0.0

            if hasattr(self.data_manager, "get_incomes"):
                for t in self.data_manager.get_incomes():
                    amount = float(getattr(t, "amount", 0.0))
                    total_income += amount

            if hasattr(self.data_manager, "get_expenses"):
                for t in self.data_manager.get_expenses():
                    amount = float(getattr(t, "amount", 0.0))
                    total_expenses += amount

            balance = total_income - total_expenses

            self.summary_label.setText(
                f"Income: {total_income:,.2f} | Expenses: {total_expenses:,.2f} | "
                f"<b>Balance: {balance:,.2f}</b>"
            )
        except Exception:
            self.summary_label.setText("Summary unavailable")

    def _touch_last_saved(self) -> None:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_saved_label.setText(f"Last saved: {now}")

    def _set_status(self, text: str) -> None:
        if self.status is not None:
            self.status.showMessage(text, 3000)
