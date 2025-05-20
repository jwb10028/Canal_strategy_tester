# ui/data_panel.py

import os
import webbrowser
from ui.frame import FramelessWindow
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox,
    QPushButton, QFileDialog, QMessageBox
)
from PyQt5.QtCore import QStandardPaths


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
        self.source_dropdown.addItems(["yfinance", "CSV File"])
        layout.addWidget(self.source_dropdown)

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

    def get_cache_path(self):
        cache_dir = os.path.join(QStandardPaths.writableLocation(QStandardPaths.CacheLocation), "quantback_cache")
        os.makedirs(cache_dir, exist_ok=True)
        return cache_dir

    def cache_data(self):
        QMessageBox.information(self, "Cache", "Data cached successfully (placeholder).")

    def clear_cache(self):
        path = self.get_cache_path()
        try:
            for file in os.listdir(path):
                os.remove(os.path.join(path, file))
            QMessageBox.information(self, "Cache Cleared", "All cache files have been deleted.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not clear cache: {e}")

    def view_cache(self):
        path = self.get_cache_path()
        if os.path.exists(path):
            webbrowser.open(f"file://{path}")
        else:
            QMessageBox.information(self, "Cache Directory", "Cache directory does not exist.")
