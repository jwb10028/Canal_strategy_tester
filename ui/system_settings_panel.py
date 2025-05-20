# ui/system_settings_panel.py

import os
import webbrowser
from ui.frame import FramelessWindow
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton,
    QCheckBox, QFileDialog, QMessageBox
)
from PyQt5.QtCore import QStandardPaths


class SystemSettingsDialog(FramelessWindow):
    def __init__(self):
        super().__init__(title="System Settings")
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

            QCheckBox {
                color: #f0f0f0;
                font-size: 13px;
                padding: 6px;
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

        # Theme mode
        layout.addWidget(QLabel("Theme Mode"))
        self.theme_mode = QComboBox()
        self.theme_mode.addItems(["Dark", "Light"])
        layout.addWidget(self.theme_mode)

        # Default strategy
        layout.addWidget(QLabel("Default Strategy"))
        self.default_strategy = QComboBox()
        self.default_strategy.addItems(["SMA Crossover", "RSI", "Buy & Hold"])
        layout.addWidget(self.default_strategy)

        # Default data source
        layout.addWidget(QLabel("Default Data Source"))
        self.default_data_source = QComboBox()
        self.default_data_source.addItems(["yfinance", "CSV File"])
        layout.addWidget(self.default_data_source)

        # Auto-clear cache on launch
        self.auto_clear_checkbox = QCheckBox("Auto-clear cache on launch")
        layout.addWidget(self.auto_clear_checkbox)

        # Developer mode
        self.dev_mode_checkbox = QCheckBox("Enable developer mode")
        layout.addWidget(self.dev_mode_checkbox)

        # Set custom cache dir
        self.set_cache_btn = QPushButton("Set Custom Cache Directory")
        self.set_cache_btn.clicked.connect(self.set_cache_dir)
        layout.addWidget(self.set_cache_btn)

        # Open logs folder
        self.open_logs_btn = QPushButton("Open Logs Folder")
        self.open_logs_btn.clicked.connect(self.open_logs)
        layout.addWidget(self.open_logs_btn)

        # Reset all settings
        self.reset_btn = QPushButton("Reset All Preferences")
        self.reset_btn.clicked.connect(self.reset_settings)
        layout.addWidget(self.reset_btn)

        # Close
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        form = QWidget()
        form.setLayout(layout)
        self.add_body_widget(form)

    def set_cache_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Cache Directory")
        if directory:
            QMessageBox.information(self, "Set Cache", f"Cache path set to:\n{directory}")

    def open_logs(self):
        log_dir = os.path.join(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation), "logs")
        os.makedirs(log_dir, exist_ok=True)
        webbrowser.open(f"file://{log_dir}")

    def reset_settings(self):
        self.theme_mode.setCurrentIndex(0)
        self.default_strategy.setCurrentIndex(0)
        self.default_data_source.setCurrentIndex(0)
        self.auto_clear_checkbox.setChecked(False)
        self.dev_mode_checkbox.setChecked(False)
        QMessageBox.information(self, "Preferences Reset", "All preferences have been reset to default.")
