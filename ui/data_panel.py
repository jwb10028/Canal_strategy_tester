# ui/data_panel.py

import os
import webbrowser
from ui.frame import FramelessWindow
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox,
    QPushButton, QFileDialog, QMessageBox, QLineEdit
)
from PyQt5.QtCore import QStandardPaths
from data.data_service import DataService


class DataLayerDialog(FramelessWindow):
    def __init__(self):
        super().__init__(title="Data Layer Settings")
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

            QComboBox {
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
                border-radius: 4px;
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

        # Data source selection
        layout.addWidget(QLabel("Select Data Source"))
        self.source_dropdown = QComboBox()
        self.source_dropdown.addItems(["yfinance", "CSV File", "investing.com", "Custom"])
        self.source_dropdown.currentTextChanged.connect(self.on_source_changed)
        layout.addWidget(self.source_dropdown)

        # CSV file picker (hidden by default)
        self.csv_button = QPushButton("Select CSV File")
        self.csv_button.clicked.connect(self.select_csv_file)
        self.csv_button.setVisible(False)
        layout.addWidget(self.csv_button)

        # Investing.com country input (hidden by default)
        self.country_label = QLabel("Investing.com Country")
        self.country_label.setVisible(False)
        layout.addWidget(self.country_label)
        self.country_input = QLineEdit()
        self.country_input.setPlaceholderText("e.g. united states")
        self.country_input.setVisible(False)
        layout.addWidget(self.country_input)

        # Custom API endpoint and key (hidden by default)
        self.custom_api_label = QLabel("Custom API Endpoint")
        self.custom_api_label.setVisible(False)
        layout.addWidget(self.custom_api_label)
        self.custom_api_input = QLineEdit()
        self.custom_api_input.setPlaceholderText("https://api.example.com/data")
        self.custom_api_input.setVisible(False)
        layout.addWidget(self.custom_api_input)
        self.custom_key_label = QLabel("API Key")
        self.custom_key_label.setVisible(False)
        layout.addWidget(self.custom_key_label)
        self.custom_key_input = QLineEdit()
        self.custom_key_input.setPlaceholderText("Your API Key")
        self.custom_key_input.setVisible(False)
        layout.addWidget(self.custom_key_input)

        # Apply button
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_settings)
        layout.addWidget(self.apply_button)

        # Cache action buttons
        self.cache_button = QPushButton("Cache Current Data")
        self.cache_button.clicked.connect(self.cache_data)
        layout.addWidget(self.cache_button)

        self.clear_cache_button = QPushButton("Clear Cache")
        self.clear_cache_button.clicked.connect(self.clear_cache)
        layout.addWidget(self.clear_cache_button)

        self.view_cache_button = QPushButton("View Cache Directory")
        self.view_cache_button.clicked.connect(self.view_cache)
        layout.addWidget(self.view_cache_button)

        # Close
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        # Final layout
        form = QWidget()
        form.setLayout(layout)
        self.add_body_widget(form)

        # Internal state for settings
        self._pending_source = DataService.get_data_source()
        self._pending_csv_path = getattr(DataService, '_csv_path', None)
        self._pending_country = "united states"
        self._pending_custom_api_endpoint = None
        self._pending_custom_api_key = None
        self.source_dropdown.setCurrentText(self._pending_source)
        if self._pending_source == "CSV File":
            self.csv_button.setVisible(True)
        else:
            self.csv_button.setVisible(False)
        if self._pending_source == "investing.com":
            self.country_label.setVisible(True)
            self.country_input.setVisible(True)
        else:
            self.country_label.setVisible(False)
            self.country_input.setVisible(False)
        if self._pending_source == "Custom":
            self.custom_api_label.setVisible(True)
            self.custom_api_input.setVisible(True)
            self.custom_key_label.setVisible(True)
            self.custom_key_input.setVisible(True)
        else:
            self.custom_api_label.setVisible(False)
            self.custom_api_input.setVisible(False)
            self.custom_key_label.setVisible(False)
            self.custom_key_input.setVisible(False)

    def on_source_changed(self, text):
        self._pending_source = text
        if text == "CSV File":
            self.csv_button.setVisible(True)
            self.country_label.setVisible(False)
            self.country_input.setVisible(False)
            self.custom_api_label.setVisible(False)
            self.custom_api_input.setVisible(False)
            self.custom_key_label.setVisible(False)
            self.custom_key_input.setVisible(False)
            self._pending_country = None
            self._pending_custom_api_endpoint = None
            self._pending_custom_api_key = None
        elif text == "investing.com":
            self.csv_button.setVisible(False)
            self.country_label.setVisible(True)
            self.country_input.setVisible(True)
            self.custom_api_label.setVisible(False)
            self.custom_api_input.setVisible(False)
            self.custom_key_label.setVisible(False)
            self.custom_key_input.setVisible(False)
            self._pending_csv_path = None
            self._pending_custom_api_endpoint = None
            self._pending_custom_api_key = None
        elif text == "Custom":
            self.csv_button.setVisible(False)
            self.country_label.setVisible(False)
            self.country_input.setVisible(False)
            self.custom_api_label.setVisible(True)
            self.custom_api_input.setVisible(True)
            self.custom_key_label.setVisible(True)
            self.custom_key_input.setVisible(True)
            self._pending_csv_path = None
            self._pending_country = None
        else:
            self.csv_button.setVisible(False)
            self.country_label.setVisible(False)
            self.country_input.setVisible(False)
            self.custom_api_label.setVisible(False)
            self.custom_api_input.setVisible(False)
            self.custom_key_label.setVisible(False)
            self.custom_key_input.setVisible(False)
            self._pending_csv_path = None
            self._pending_country = None
            self._pending_custom_api_endpoint = None
            self._pending_custom_api_key = None

    def select_csv_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if path:
            self._pending_csv_path = path
        else:
            # If user cancels, revert to yfinance
            self.source_dropdown.setCurrentText("yfinance")

    def apply_settings(self):
        if self._pending_source == "CSV File" and not self._pending_csv_path:
            QMessageBox.warning(self, "Missing CSV File", "Please select a CSV file for CSV data source.")
            return
        if self._pending_source == "investing.com":
            country = self.country_input.text().strip() or "united states"
            self._pending_country = country
            DataService.set_data_source(self._pending_source, investing_country=country)
        elif self._pending_source == "Custom":
            endpoint = self.custom_api_input.text().strip()
            key = self.custom_key_input.text().strip()
            if not endpoint or not key:
                QMessageBox.warning(self, "Missing Info", "Please enter both endpoint and API key.")
                return
            self._pending_custom_api_endpoint = endpoint
            self._pending_custom_api_key = key
            DataService.set_data_source(self._pending_source, custom_api_endpoint=endpoint, custom_api_key=key)
        else:
            DataService.set_data_source(self._pending_source, csv_path=self._pending_csv_path)
        QMessageBox.information(self, "Settings Applied", "Data source settings have been applied.")

    def get_cache_path(self):
        cache_dir = os.path.join(QStandardPaths.writableLocation(QStandardPaths.CacheLocation), "quantback_cache")
        os.makedirs(cache_dir, exist_ok=True)
        return cache_dir

    def cache_data(self):
        if DataService.cache_data():
            QMessageBox.information(self, "Cache", "Data cached successfully (placeholder).")
        else:
            QMessageBox.warning(self, "Cache", "Failed to cache data.")

    def clear_cache(self):
        success, error = DataService.clear_cache()
        if success:
            QMessageBox.information(self, "Cache Cleared", "All cache files have been deleted.")
        else:
            QMessageBox.warning(self, "Error", f"Could not clear cache: {error}")

    def view_cache(self):
        if not DataService.view_cache():
            QMessageBox.information(self, "Cache Directory", "Cache directory does not exist.")
        else:
            path = self.get_cache_path()
            if os.path.exists(path):
                webbrowser.open(f"file://{path}")
            else:
                QMessageBox.information(self, "Cache Directory", "Cache directory does not exist.")
