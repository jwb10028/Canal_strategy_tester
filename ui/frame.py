# ui/frameless_window.py

from PyQt5.QtWidgets import (
    QDialog, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QWidget
)
from PyQt5.QtCore import Qt, QPoint


class FramelessWindow(QDialog):
    def __init__(self, title="Window"):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("""
            QDialog {
                background-color: #393939;
                border: 1px solid #5a5a5a;
                border-radius: 8px;
            }
            QLabel {
                color: #f0f0f0;
                font-weight: bold;
            }
            QPushButton {
                background-color: transparent;
                color: #f0f0f0;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                color: #ff5555;
            }
        """)

        self.drag_pos = None

        # Title bar
        self.header = QWidget()
        header_layout = QHBoxLayout()
        self.title_label = QLabel(title)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        self.min_btn = QPushButton("—")
        self.min_btn.clicked.connect(self.showMinimized)
        header_layout.addWidget(self.min_btn)

        self.close_btn = QPushButton("✕")
        self.close_btn.clicked.connect(self.close)
        header_layout.addWidget(self.close_btn)

        self.header.setLayout(header_layout)
        self.header.setFixedHeight(50)

        # Container layout
        self.container_layout = QVBoxLayout()
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.addWidget(self.header)

        self.setLayout(self.container_layout)

    def add_body_widget(self, widget):
        """Add your form or content widget here"""
        self.container_layout.addWidget(widget)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_pos and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()
