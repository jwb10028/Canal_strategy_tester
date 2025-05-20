# ui/strategy_panel.py


from ui.frame import FramelessWindow
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton
)

class StrategyEngineDialog(FramelessWindow):
    def __init__(self):
        super().__init__(title="Strategy Engine")
        self.setFixedWidth(400)

        self.setStyleSheet("""
            QDialog, QWidget {
                background-color: #393939;
                border: 1px solid #5a5a5a;
                border-radius: 8px;
                padding: 16px;
            }

            QLabel {
                color: #f0f0f0;
                font-size: 13px;
                padding-bottom: 4px;
            }

            QLineEdit, QComboBox {
                background-color: #2e2e2e;
                color: #f0f0f0;
                border: 1px solid #5a5a5a;
                border-radius: 4px;
                padding: 6px;
                font-size: 13px;
                min-height: 28px;
            }

            QPushButton {
                background-color: #3d3d3d;
                color: #f0f0f0;
                border: 1px solid #5a5a5a;
                border-radius: 6px;
                padding: 6px 12px;
                margin-top: 10px;
            }

            QPushButton:hover {
                background-color: #4c4c4c;
            }

            QPushButton:pressed {
                background-color: #5e5e5e;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(12)

        # Strategy dropdown
        layout.addWidget(QLabel("Strategy Type"))
        self.strategy_dropdown = QComboBox()
        self.strategy_dropdown.addItems(["SMA Crossover", "RSI", "Buy & Hold"])
        self.strategy_dropdown.currentTextChanged.connect(self.update_config_fields)
        layout.addWidget(self.strategy_dropdown)

        # Dynamic config section
        self.config_section = QVBoxLayout()
        layout.addLayout(self.config_section)

        # Lock + Close buttons
        self.lock_btn = QPushButton("Lock Strategy")
        self.lock_btn.clicked.connect(self.lock_strategy)
        layout.addWidget(self.lock_btn)

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        layout.addWidget(self.close_btn)

        # Root form
        form = QWidget()
        form.setLayout(layout)
        self.add_body_widget(form)

        self.update_config_fields("SMA Crossover")

    def update_config_fields(self, strategy_name):
        # Clear old widgets
        while self.config_section.count():
            child = self.config_section.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Add new fields depending on strategy
        if strategy_name == "SMA Crossover":
            self.short_window = QLineEdit()
            self.short_window.setPlaceholderText("Short window (e.g. 10)")
            self.config_section.addWidget(QLabel("Short Window"))
            self.config_section.addWidget(self.short_window)

            self.long_window = QLineEdit()
            self.long_window.setPlaceholderText("Long window (e.g. 30)")
            self.config_section.addWidget(QLabel("Long Window"))
            self.config_section.addWidget(self.long_window)

        elif strategy_name == "RSI":
            self.rsi_period = QLineEdit()
            self.rsi_period.setPlaceholderText("RSI period (e.g. 14)")
            self.config_section.addWidget(QLabel("RSI Period"))
            self.config_section.addWidget(self.rsi_period)

        # Buy & Hold requires no inputs

    def get_config(self):
        strategy = self.strategy_dropdown.currentText()
        config = {"strategy": strategy}

        if strategy == "SMA Crossover":
            config["short_window"] = int(self.short_window.text()) if self.short_window.text().isdigit() else 10
            config["long_window"] = int(self.long_window.text()) if self.long_window.text().isdigit() else 30

        elif strategy == "RSI":
            config["rsi_period"] = int(self.rsi_period.text()) if self.rsi_period.text().isdigit() else 14

        return config

    def lock_strategy(self):
        self.accept()

