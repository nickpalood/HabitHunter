from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

class DashboardTab(QWidget):
    def __init__(self, data_manager=None, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Dashboard Overview (placeholder)"))
