import sys
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QGridLayout, QDialog, QVBoxLayout as QVBox, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
import pyqtgraph as pg
from pyqtgraph import InfiniteLine, DateAxisItem

from ui.frame import FramelessWindow
from ui.user_input_panel import UserInputDialog
from ui.strategy_panel import StrategyEngineDialog
from ui.data_panel import DataLayerDialog
from ui.system_settings_panel import SystemSettingsDialog
from core import strategy as strategy_module
from core import backtest as backtest_module
import yfinance as yf
import pandas as pd


class MainWindow(FramelessWindow):
    def __init__(self):
        super().__init__(title="Canalytics")
        self.setMinimumSize(1280, 720)

        body = QWidget()
        main_layout = QVBoxLayout()
        body.setLayout(main_layout)

        # Header Buttons
        header_layout = QHBoxLayout()
        buttons = {
            "User Input": lambda: self.open_modal("User Input", "User input panel goes here."),
            "Strategy": lambda: self.open_modal("Strategy", "Strategy selection panel goes here."),
            "Data": lambda: self.open_modal("Data", "Data layer settings go here."),
            "System": lambda: self.open_modal("System", "System settings go here.")
        }

        button_style = """
            QPushButton {
                background-color: #3d3d3d;
                color: #f0f0f0;
                border: 1px solid #5a5a5a;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #4c4c4c;
            }
            QPushButton:pressed {
                background-color: #5e5e5e;
            }
        """

        for label, callback in buttons.items():
            btn = QPushButton(label)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(button_style)
            btn.clicked.connect(callback)
            header_layout.addWidget(btn)

        header_layout.addSpacerItem(QSpacerItem(40, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))

        run_button = QPushButton("Run Backtest")
        run_button.setCursor(Qt.PointingHandCursor)
        run_button.setStyleSheet(button_style)
        run_button.clicked.connect(self.run_backtest)
        header_layout.addWidget(run_button)

        main_layout.addLayout(header_layout)

        # Plot with date axis
        date_axis = DateAxisItem(orientation='bottom')
        self.plot_widget = pg.PlotWidget(axisItems={'bottom': date_axis})
        self.plot_widget.setBackground("#1e1e1e")
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('left', "")
        self.plot_widget.setLabel('bottom', "")
        plot_item = self.plot_widget.getPlotItem()
        plot_item.setTitle("")
        plot_item.getAxis('left').setPen('#f0f0f0')
        plot_item.getAxis('bottom').setPen('#f0f0f0')
        main_layout.addWidget(self.plot_widget)
        self.plot_placeholder()

        # Metrics
        metrics_layout = QGridLayout()
        self.metrics = {
            "Total Return": QLabel("--"),
            "Sharpe Ratio": QLabel("--"),
            "Max Drawdown": QLabel("--")
        }
        for row, (name, label) in enumerate(self.metrics.items()):
            metrics_layout.addWidget(QLabel(f"{name}:"), row, 0)
            metrics_layout.addWidget(label, row, 1)
        main_layout.addLayout(metrics_layout)

        self.add_body_widget(body)

    def plot_placeholder(self):
        x = [0, 1, 2, 3, 4, 5]
        y = [100, 105, 103, 110, 108, 115]
        self.plot_widget.plot(x, y, pen=pg.mkPen(color="#4fc3f7", width=2), symbol='o', symbolBrush="#4fc3f7")

    def open_modal(self, title, content):
        dialog = None
        if title == "User Input":
            dialog = UserInputDialog()
            if dialog.exec_() == QDialog.Accepted:
                self.input_config = dialog.get_config()
        elif title == "Strategy":
            dialog = StrategyEngineDialog()
            if dialog.exec_() == QDialog.Accepted:
                self.strategy_config = dialog.get_config()
            else:
                self.strategy_config = None
        elif title == "Data":
            dialog = DataLayerDialog()
        elif title == "System":
            dialog = SystemSettingsDialog()

        if dialog:
            dialog.exec_()

    def run_backtest(self):
        user_cfg = getattr(self, 'input_config', None)
        strat_cfg = getattr(self, 'strategy_config', None)

        if not user_cfg or not strat_cfg:
            print("Missing config")
            return

        ticker = user_cfg["ticker"]
        start = user_cfg["start_date"]
        end = user_cfg["end_date"]

        df = yf.download(ticker, start=start, end=end)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if df.empty:
            print("Failed to download data")
            return

        strat = strat_cfg["strategy"]
        if strat == "SMA Crossover":
            signals = strategy_module.sma_crossover_strategy(df, strat_cfg["short_window"], strat_cfg["long_window"])
        elif strat == "RSI":
            signals = strategy_module.rsi_strategy(df, period=strat_cfg.get("rsi_period", 14))
        elif strat == "Buy & Hold":
            signals = strategy_module.buy_and_hold_strategy(df)
        else:
            print("Unknown strategy")
            return

        portfolio = backtest_module.run_backtest(
            df,
            signals,
            initial_capital=user_cfg["initial_capital"],
            position_size_pct=user_cfg["position_size"]
        )

        x = [ts.timestamp() for ts in portfolio.index]
        y = portfolio["total"].values

        self.plot_widget.clear()
        self.plot_widget.plot(x, y, pen=pg.mkPen(color="#4fc3f7", width=2))

        prev_pos = 0
        for i in range(len(portfolio)):
            pos = portfolio["position"].iloc[i]
            ts = portfolio.index[i].timestamp()

            if pos > prev_pos:
                line = InfiniteLine(pos=ts, angle=90, pen=pg.mkPen('b', width=1.5, style=Qt.DashLine), movable=False)
                self.plot_widget.addItem(line)
            elif pos < prev_pos:
                line = InfiniteLine(pos=ts, angle=90, pen=pg.mkPen('r', width=1.5, style=Qt.DashLine), movable=False)
                self.plot_widget.addItem(line)
            prev_pos = pos

        # Final exit line at end_date
        try:
            end_ts = datetime.strptime(user_cfg["end_date"], "%Y-%m-%d").timestamp()
            line = InfiniteLine(pos=end_ts, angle=90, pen=pg.mkPen('r', width=1.5, style=Qt.DashLine), movable=False)
            self.plot_widget.addItem(line)
        except Exception as e:
            print("Could not parse end date:", e)

        total_return = (portfolio["total"].iloc[-1] - portfolio["total"].iloc[0]) / portfolio["total"].iloc[0]
        self.metrics["Total Return"].setText(f"{total_return:.2%}")
        self.metrics["Sharpe Ratio"].setText("--")
        self.metrics["Max Drawdown"].setText("--")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
