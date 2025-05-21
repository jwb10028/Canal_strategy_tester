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

        # Metrics layout (grid)
        from PyQt5.QtWidgets import QScrollArea, QFrame

        self.metrics_container = QWidget()
        self.metrics_layout = QGridLayout()
        self.metrics_container.setLayout(self.metrics_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedHeight(180)
        self.scroll_area.setWidget(self.metrics_container)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        main_layout.addWidget(self.scroll_area)

        self.add_body_widget(body)

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
            dialog.exec_()
        elif title == "System":
            dialog = SystemSettingsDialog()
            dialog.exec_()

    def run_backtest(self):
        user_cfg = getattr(self, 'input_config', None)
        strat_cfg = getattr(self, 'strategy_config', None)

        if not user_cfg or not strat_cfg:
            print("Missing config")
            return

        tickers = user_cfg.get("tickers", [])
        start = user_cfg["start_date"]
        end = user_cfg["end_date"]

        self.plot_widget.clear()
        self.results = {}
        colors = ['#4fc3f7', '#ff8a65', '#9575cd', '#81c784', '#f06292', '#ffd54f', '#64b5f6', '#e57373', '#a1887f', '#4db6ac']

        for i, ticker in enumerate(tickers):
            df = yf.download(ticker, start=start, end=end)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            if df.empty:
                print(f"Failed to download data for {ticker}")
                continue

            strat = strat_cfg["strategy"]
            if strat == "SMA Crossover":
                signals = strategy_module.sma_crossover_strategy(df, strat_cfg["short_window"], strat_cfg["long_window"])
            elif strat == "RSI":
                signals = strategy_module.rsi_strategy(df, period=strat_cfg.get("rsi_period", 14))
            elif strat == "Buy & Hold":
                signals = strategy_module.buy_and_hold_strategy(df)
            else:
                print("Unknown strategy")
                continue

            portfolio = backtest_module.run_backtest(
                df,
                signals,
                initial_capital=user_cfg["initial_capital"],
                position_size_pct=user_cfg["position_size"]
            )

            x = [ts.timestamp() for ts in portfolio.index]
            y = portfolio["total"].values
            color = colors[i % len(colors)]
            plot = self.plot_widget.plot(x, y, pen=pg.mkPen(color=color, width=2), name=ticker)

            returns = portfolio["total"].pct_change().dropna()
            sharpe = (returns.mean() / returns.std()) * (252 ** 0.5) if not returns.empty else 0.0
            peak = portfolio["total"].cummax()
            drawdown = ((portfolio["total"] - peak) / peak).min()
            total_return = (portfolio["total"].iloc[-1] - portfolio["total"].iloc[0]) / portfolio["total"].iloc[0]

            # Draw entry/exit markers
            prev_pos = 0
            for j in range(len(portfolio)):
                pos = portfolio["position"].iloc[j]
                ts = portfolio.index[j].timestamp()
                val = portfolio["total"].iloc[j]
                if pos > prev_pos:
                    entry = pg.ScatterPlotItem([ts], [val], symbol='t1', size=8, brush='g')
                    self.plot_widget.addItem(entry)
                elif pos < prev_pos:
                    exit_ = pg.ScatterPlotItem([ts], [val], symbol='t', size=8, brush='r')
                    self.plot_widget.addItem(exit_)
                prev_pos = pos

            self.results[ticker] = {
                "return": total_return,
                "sharpe": sharpe,
                "drawdown": drawdown
            }

        try:
            end_ts = datetime.strptime(user_cfg["end_date"], "%Y-%m-%d").timestamp()
            line = InfiniteLine(pos=end_ts, angle=90, pen=pg.mkPen('r', width=1.5, style=Qt.DashLine), movable=False)
            self.plot_widget.addItem(line)
        except Exception as e:
            print("Could not parse end date:", e)

        # Clear metrics layout and display results
        for i in reversed(range(self.metrics_layout.count())):
            widget = self.metrics_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        for row, (ticker, stats) in enumerate(self.results.items()):
            color = colors[row % len(colors)]
            style = f"color: {color}; font-weight: bold;"
        
            self.metrics_layout.addWidget(QLabel(f"{ticker} Return:"), row * 3, 0)
            return_label = QLabel(f"{stats['return']:.2%}")
            return_label.setStyleSheet(style)
            self.metrics_layout.addWidget(return_label, row * 3, 1)
        
            self.metrics_layout.addWidget(QLabel(f"{ticker} Sharpe:"), row * 3 + 1, 0)
            sharpe_label = QLabel(f"{stats['sharpe']:.2f}")
            sharpe_label.setStyleSheet(style)
            self.metrics_layout.addWidget(sharpe_label, row * 3 + 1, 1)
        
            self.metrics_layout.addWidget(QLabel(f"{ticker} Max Drawdown:"), row * 3 + 2, 0)
            drawdown_label = QLabel(f"{stats['drawdown']:.2%}")
            drawdown_label.setStyleSheet(style)
            self.metrics_layout.addWidget(drawdown_label, row * 3 + 2, 1)

            self.metrics_layout.addWidget(QLabel(f"{ticker} Sharpe:"), row * 3 + 1, 0)
            self.metrics_layout.addWidget(QLabel(f"{stats['sharpe']:.2f}"), row * 3 + 1, 1)

            self.metrics_layout.addWidget(QLabel(f"{ticker} Max Drawdown:"), row * 3 + 2, 0)
            self.metrics_layout.addWidget(QLabel(f"{stats['drawdown']:.2%}"), row * 3 + 2, 1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
