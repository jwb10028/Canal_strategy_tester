# core/strategy.py

import pandas as pd


def sma_crossover_strategy(df, short_window=10, long_window=30):
    """
    Simple Moving Average Crossover strategy.
    Buy when short MA crosses above long MA, sell when below.

    Returns a Series of signals: 1 = Buy, -1 = Sell, 0 = Hold
    """
    df = df.copy()
    df['short_ma'] = df['Close'].rolling(window=short_window, min_periods=1).mean()
    df['long_ma'] = df['Close'].rolling(window=long_window, min_periods=1).mean()

    signal = pd.Series(index=df.index, data=0)

    # Generate signals
    signal[df['short_ma'] > df['long_ma']] = 1
    signal[df['short_ma'] < df['long_ma']] = -1

    # Only change when crossing
    signal = signal.diff().fillna(0)
    signal[signal != 0] = signal[signal != 0].apply(lambda x: 1 if x > 0 else -1)

    return signal


def rsi_strategy(df, period=14, threshold_low=30, threshold_high=70):
    """
    RSI strategy: Buy when RSI < threshold_low, Sell when RSI > threshold_high
    """
    df = df.copy()

    # 🔐 Flatten MultiIndex columns if needed
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    assert "Close" in df.columns, "DataFrame must contain 'Close' column"

    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()

    rs = avg_gain / avg_loss.replace(0, 1e-10)
    rsi = 100 - (100 / (1 + rs))

    # Ensure alignment
    rsi = rsi.reindex(df.index)
    signal = pd.Series(0, index=df.index)

    signal[rsi < threshold_low] = 1
    signal[rsi > threshold_high] = -1

    return signal


def buy_and_hold_strategy(df):
    """
    Buy at the start, hold forever.
    """
    signal = pd.Series(0, index=df.index)
    signal.iloc[0] = 1  # Buy at start
    return signal
