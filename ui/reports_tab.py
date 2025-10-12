from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

class ReportsTab(QWidget):
    def __init__(self, data_manager=None, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Reports Tab (placeholder)"))
