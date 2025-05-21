import os
import webbrowser
import pandas as pd
import yfinance as yf
import investpy
from PyQt5.QtCore import QStandardPaths

class DataService:
    _data_source = "yfinance"  # Default source
    _csv_path = None
    _investing_country = "united states"  # Default country for investpy
    _custom_api_endpoint = None
    _custom_api_key = None

    @staticmethod
    def set_data_source(source, csv_path=None, investing_country=None, custom_api_endpoint=None, custom_api_key=None):
        DataService._data_source = source
        if source == "CSV File" and csv_path:
            DataService._csv_path = csv_path
        if source == "investing.com" and investing_country:
            DataService._investing_country = investing_country
        if source == "Custom" and custom_api_endpoint and custom_api_key:
            DataService._custom_api_endpoint = custom_api_endpoint
            DataService._custom_api_key = custom_api_key

    @staticmethod
    def get_data_source():
        return DataService._data_source

    @staticmethod
    def get_cache_path():
        cache_dir = os.path.join(QStandardPaths.writableLocation(QStandardPaths.CacheLocation), "quantback_cache")
        os.makedirs(cache_dir, exist_ok=True)
        return cache_dir

    @staticmethod
    def cache_data():
        # Placeholder for actual caching logic
        return True

    @staticmethod
    def clear_cache():
        path = DataService.get_cache_path()
        try:
            for file in os.listdir(path):
                os.remove(os.path.join(path, file))
            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def view_cache():
        path = DataService.get_cache_path()
        if os.path.exists(path):
            webbrowser.open(f"file://{path}")
            return True
        return False

    @staticmethod
    def load_data(ticker, start, end):
        if DataService._data_source == "yfinance":
            df = yf.download(ticker, start=start, end=end)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            return df
        elif DataService._data_source == "CSV File" and DataService._csv_path:
            try:
                df = pd.read_csv(DataService._csv_path, parse_dates=True, index_col=0)
                # Optionally filter by ticker, start, end if present in CSV
                if ticker in df.columns or "Ticker" in df.columns:
                    # If multi-ticker CSV, filter here
                    pass
                # Optionally filter by date range
                if start and end:
                    df = df.loc[start:end]
                return df
            except Exception as e:
                print(f"Failed to load CSV: {e}")
                return pd.DataFrame()
        elif DataService._data_source == "investing.com":
            try:
                # investpy expects date strings in 'dd/mm/yyyy' format
                start_fmt = pd.to_datetime(start).strftime('%d/%m/%Y')
                end_fmt = pd.to_datetime(end).strftime('%d/%m/%Y')
                df = investpy.get_stock_historical_data(
                    stock=ticker,
                    country=DataService._investing_country,
                    from_date=start_fmt,
                    to_date=end_fmt
                )
                return df
            except Exception as e:
                print(f"Failed to load data from investing.com: {e}")
                return pd.DataFrame()
        elif DataService._data_source == "Custom" and DataService._custom_api_endpoint and DataService._custom_api_key:
            import requests
            try:
                params = {
                    "ticker": ticker,
                    "start": start,
                    "end": end,
                    "apikey": DataService._custom_api_key
                }
                response = requests.get(DataService._custom_api_endpoint, params=params)
                response.raise_for_status()
                # Try to parse as DataFrame
                try:
                    df = pd.read_json(response.text)
                except Exception:
                    df = pd.DataFrame(response.json())
                return df
            except Exception as e:
                print(f"Failed to load data from custom API: {e}")
                return pd.DataFrame()
        else:
            return pd.DataFrame()