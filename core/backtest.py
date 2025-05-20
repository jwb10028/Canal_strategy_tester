# core/backtester.py

import pandas as pd


def run_backtest(df, signals, initial_capital=10000, position_size_pct=10):
    """
    Run a basic backtest using provided signals and user config.
    
    Arguments:
        df: DataFrame with 'Close' price
        signals: Series with 1 (buy), -1 (sell), 0 (hold)
        initial_capital: starting capital
        position_size_pct: percentage of capital to use per trade

    Returns:
        portfolio: DataFrame with equity curve and positions
    """
    df = df.copy()
    signals = signals.reindex(df.index).fillna(0)

    capital = initial_capital
    position_size = capital * (position_size_pct / 100)
    cash = capital
    position = 0
    portfolio = []

    for i in range(len(df)):
        price = float(df['Close'].iloc[i])
        signal = signals.iloc[i]

        # Buy
        if signal == 1 and cash >= price:
            shares = position_size // price
            cost = shares * price
            cash -= cost
            position += shares

        # Sell
        elif signal == -1 and position > 0:
            cash += position * price
            position = 0

        value = cash + (position * price)
        portfolio.append({
            'date': df.index[i],
            'price': price,
            'cash': cash,
            'position': position,
            'total': value
        })

    portfolio_df = pd.DataFrame(portfolio).set_index('date')
    return portfolio_df
