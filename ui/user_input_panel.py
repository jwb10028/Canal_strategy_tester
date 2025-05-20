from ui.frame import FramelessWindow
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QDateEdit, QPushButton, QListWidget, QListWidgetItem, QHBoxLayout
)
from PyQt5.QtCore import QDate


class UserInputDialog(FramelessWindow):
    def __init__(self):
        super().__init__(title="User Input Panel")
        self.setFixedWidth(400)

        self.tickers = []

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

            QLineEdit, QDateEdit {
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

        # Stock ticker input
        layout.addWidget(QLabel("Add Ticker"))
        ticker_input_layout = QHBoxLayout()
        self.ticker_input = QLineEdit()
        self.ticker_input.setPlaceholderText("e.g. AAPL, MSFT")
        ticker_input_layout.addWidget(self.ticker_input)
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_ticker)
        ticker_input_layout.addWidget(add_btn)
        layout.addLayout(ticker_input_layout)

        self.ticker_list = QListWidget()
        layout.addWidget(self.ticker_list)

        # Start date
        layout.addWidget(QLabel("Start Date"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        layout.addWidget(self.start_date)

        # End date
        layout.addWidget(QLabel("End Date"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        layout.addWidget(self.end_date)

        # Initial capital
        layout.addWidget(QLabel("Initial Capital ($, optional)"))
        self.initial_capital = QLineEdit()
        self.initial_capital.setPlaceholderText("e.g. 10000")
        layout.addWidget(self.initial_capital)

        # Position size
        layout.addWidget(QLabel("Position Size (%, optional)"))
        self.position_size = QLineEdit()
        self.position_size.setPlaceholderText("e.g. 10")
        layout.addWidget(self.position_size)

        # Lock button
        lock_btn = QPushButton("Lock Inputs")
        lock_btn.clicked.connect(self.lock_inputs)
        layout.addWidget(lock_btn)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        form = QWidget()
        form.setLayout(layout)
        self.add_body_widget(form)

    def add_ticker(self):
        text = self.ticker_input.text().strip().upper()
        if text and text not in self.tickers and len(self.tickers) < 10:
            self.tickers.append(text)
            item = QListWidgetItem(text)
            del_btn = QPushButton("x")
            del_btn.setMaximumWidth(20)
            del_btn.clicked.connect(lambda _, t=text: self.remove_ticker(t))
            self.ticker_list.addItem(item)

    def remove_ticker(self, ticker):
        if ticker in self.tickers:
            self.tickers.remove(ticker)
            for i in range(self.ticker_list.count()):
                if self.ticker_list.item(i).text() == ticker:
                    self.ticker_list.takeItem(i)
                    break

    def get_config(self):
        return {
            "tickers": self.tickers,
            "start_date": self.start_date.date().toString("yyyy-MM-dd"),
            "end_date": self.end_date.date().toString("yyyy-MM-dd"),
            "initial_capital": float(self.initial_capital.text()) if self.initial_capital.text().isdigit() else 10000,
            "position_size": float(self.position_size.text()) if self.position_size.text().isdigit() else 10.0,
        }

    def lock_inputs(self):
        print("Inputs locked:", self.get_config())
        self.accept()
