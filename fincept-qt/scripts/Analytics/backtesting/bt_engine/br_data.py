"""
Backtrader Data Module - Fetch and prepare market data for backtesting

Supports:
- A-shares (Shanghai/Shenzhen) via AkShare
- HK stocks via AkShare
- China futures via AkShare
- US stocks via yfinance (fallback)
"""

import sys
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime


# Track if last fetch used synthetic data
_last_fetch_synthetic = False


def was_last_fetch_synthetic() -> bool:
    """Check if the last data fetch used synthetic data"""
    return _last_fetch_synthetic


def fetch_data(
    symbols: List[str],
    start_date: str,
    end_date: str,
    asset_type: str = 'stock'
) -> pd.DataFrame:
    """
    Fetch historical market data for multiple symbols

    Args:
        symbols: List of symbols (e.g., ['600519.SS', '000001.SZ'])
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        asset_type: Type of asset ('stock', 'hk_stock', 'futures')

    Returns:
        DataFrame with columns for each symbol's close prices
    """
    global _last_fetch_synthetic
    _last_fetch_synthetic = False

    try:
        import akshare as ak
    except ImportError:
        print('[BR-DATA] akshare not installed, using synthetic data', file=sys.stderr)
        _last_fetch_synthetic = True
        return _generate_synthetic_data(symbols, start_date, end_date)

    all_data = {}

    for symbol in symbols:
        try:
            df = _fetch_single_symbol(symbol, start_date, end_date, asset_type, ak)
            if df is not None and not df.empty:
                all_data[symbol] = df['close']
            else:
                print(f'[BR-DATA] No data for {symbol}', file=sys.stderr)
        except Exception as e:
            print(f'[BR-DATA] Error fetching {symbol}: {e}', file=sys.stderr)

    if not all_data:
        print('[BR-DATA] All fetches failed, using synthetic data', file=sys.stderr)
        _last_fetch_synthetic = True
        return _generate_synthetic_data(symbols, start_date, end_date)

    # Merge all symbols into single DataFrame
    result = pd.DataFrame(all_data)
    result = result.dropna()

    if result.empty:
        _last_fetch_synthetic = True
        return _generate_synthetic_data(symbols, start_date, end_date)

    return result


def fetch_ohlcv(
    symbols: List[str],
    start_date: str,
    end_date: str,
    asset_type: str = 'stock'
) -> Dict[str, pd.DataFrame]:
    """
    Fetch OHLCV data for multiple symbols

    Returns:
        Dictionary mapping symbol to DataFrame with OHLCV columns
    """
    global _last_fetch_synthetic
    _last_fetch_synthetic = False

    try:
        import akshare as ak
    except ImportError:
        print('[BR-DATA] akshare not installed', file=sys.stderr)
        _last_fetch_synthetic = True
        return {}

    result = {}

    for symbol in symbols:
        try:
            df = _fetch_single_symbol(symbol, start_date, end_date, asset_type, ak)
            if df is not None and not df.empty:
                result[symbol] = df
        except Exception as e:
            print(f'[BR-DATA] Error fetching OHLCV for {symbol}: {e}', file=sys.stderr)

    return result


def _fetch_single_symbol(
    symbol: str,
    start_date: str,
    end_date: str,
    asset_type: str,
    ak
) -> Optional[pd.DataFrame]:
    """Fetch data for a single symbol from AkShare"""

    # Parse symbol
    code = symbol.split('.')[0] if '.' in symbol else symbol

    try:
        if asset_type == 'stock' or '.SS' in symbol or '.SZ' in symbol:
            # A-share stock
            df = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start_date.replace('-', ''),
                end_date=end_date.replace('-', ''),
                adjust="qfq"  # Forward adjusted prices
            )

            if df.empty:
                return None

            # Rename columns
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '最高': 'high',
                '最低': 'low',
                '收盘': 'close',
                '成交量': 'volume',
                '成交额': 'turnover'
            })

        elif asset_type == 'hk_stock':
            # HK stock
            df = ak.stock_hk_daily(
                symbol=code,
                adjust="qfq"
            )

            if df.empty:
                return None

            # Filter by date range
            df['date'] = pd.to_datetime(df['date'])
            mask = (df['date'] >= start_date) & (df['date'] <= end_date)
            df = df[mask].copy()

            df = df.rename(columns={
                '开盘': 'open',
                '最高': 'high',
                '最低': 'low',
                '收盘': 'close',
                '成交量': 'volume'
            })

        elif asset_type == 'futures':
            # China futures
            df = ak.futures_zh_daily_sina(symbol=code)

            if df.empty:
                return None

            df['date'] = pd.to_datetime(df['date'])
            mask = (df['date'] >= start_date) & (df['date'] <= end_date)
            df = df[mask].copy()

            df = df.rename(columns={
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'volume': 'volume'
            })

        else:
            print(f'[BR-DATA] Unknown asset type: {asset_type}', file=sys.stderr)
            return None

        # Process common fields
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        # Convert to numeric types
        for col in ['open', 'high', 'low', 'close']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        if 'volume' in df.columns:
            # Handle volume strings with commas
            df['volume'] = df['volume'].astype(str).str.replace(',', '')
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce')

        # Drop any rows with NaN in critical columns
        df = df.dropna(subset=['open', 'high', 'low', 'close'])

        # Ensure we have data
        if len(df) == 0:
            return None

        return df[['open', 'high', 'low', 'close', 'volume']]

    except Exception as e:
        print(f'[BR-DATA] Exception fetching {symbol}: {e}', file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return None


def _generate_synthetic_data(
    symbols: List[str],
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """Generate synthetic price data when real data is unavailable"""
    import numpy as np

    dates = pd.bdate_range(start=start_date, end=end_date)
    n = len(dates)

    if n == 0:
        return pd.DataFrame()

    data = {}
    np.random.seed(42)  # Reproducible synthetic data

    for symbol in symbols:
        # Generate random walk with drift
        daily_returns = np.random.normal(0.0005, 0.02, n)
        prices = 100 * np.cumprod(1 + daily_returns)
        data[symbol] = prices

    return pd.DataFrame(data, index=dates)


def data_to_records(data: pd.DataFrame) -> List[Dict[str, Any]]:
    """Convert DataFrame to list of records for JSON serialization"""
    if data.empty:
        return []

    records = []
    for idx, row in data.iterrows():
        record = {'date': idx.strftime('%Y-%m-%d') if hasattr(idx, 'strftime') else str(idx)}
        for col in data.columns:
            val = row[col]
            record[col] = float(val) if pd.notna(val) else None
        records.append(record)

    return records
