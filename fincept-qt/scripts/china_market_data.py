#!/usr/bin/env python3
"""
China Market Data Unified Interface
Supports: A-Shares, HK Stocks, China Futures, Options
Compatible with Fincept Terminal DataHub architecture

Usage:
    python china_market_data.py --symbols 600519.SS,000001.SZ,rb2405 --type quote
    python china_market_data.py --symbol 600519.SS --period 1y --interval 1d --type history
"""

import sys
import json
import time
import argparse
from datetime import datetime, timedelta

try:
    import akshare as ak
    import pandas as pd
except ImportError as e:
    print(json.dumps({
        "success": False,
        "error": f"Missing dependency: {e}. Install with: pip install akshare",
        "data": []
    }))
    sys.exit(1)


def parse_symbol(symbol):
    """Parse symbol to determine market and type

    Supported formats:
    - A-Shares: 600519.SS (Shanghai), 000001.SZ (Shenzhen), 8xxxxx.BJ (Beijing)
    - HK Stocks: 0700.HK (Tencent)
    - Futures: rb2405.SHF (Rebar), IF2405.CFX (CSI300 Index Future)
    - Options: 510300C3500.SSO (ETF Option)

    Returns:
        dict with symbol, market, type info
    """
    parts = symbol.upper().split('.')
    code = parts[0]
    exchange = parts[1] if len(parts) > 1 else ''

    # Determine market type
    if exchange in ['SS', 'SH']:
        market = 'SSE'  # Shanghai Stock Exchange
        asset_type = 'stock'
    elif exchange == 'SZ':
        market = 'SZSE'  # Shenzhen Stock Exchange
        asset_type = 'stock'
    elif exchange == 'BJ':
        market = 'BSE'  # Beijing Stock Exchange
        asset_type = 'stock'
    elif exchange == 'HK':
        market = 'HKEX'  # Hong Kong Exchange
        asset_type = 'stock'
    elif exchange in ['SHF', 'CZC', 'DCE', 'CFX']:
        market = 'FUTURES'
        asset_type = 'futures'
    elif 'O' in code or 'OPTION' in exchange:
        market = 'OPTIONS'
        asset_type = 'option'
    else:
        # Default to A-share
        market = 'SSE' if code.startswith('6') else 'SZSE'
        asset_type = 'stock'

    return {
        'original': symbol,
        'code': code,
        'exchange': exchange,
        'market': market,
        'asset_type': asset_type
    }


def get_akshare_symbol(symbol_info):
    """Convert Fincept symbol format to AkShare format"""
    code = symbol_info['code']
    market = symbol_info['market']

    # A-Shares: 600519.SS -> 600519
    if market in ['SSE', 'SZSE', 'BSE']:
        return code

    # HK Stocks: 0700.HK -> hk00700
    if market == 'HKEX':
        return f"hk{code.zfill(5)}"

    # Futures: rb2405.SHF -> rb2405
    if market == 'FUTURES':
        return code

    return code


def fetch_quote_single(symbol_str):
    """Fetch realtime quote for a single Chinese stock/future

    Returns format compatible with QuoteData struct:
    {
        "symbol": "600519.SS",
        "name": "贵州茅台",
        "price": 1700.00,
        "change": 20.00,
        "change_pct": 1.19,
        "high": 1720.00,
        "low": 1680.00,
        "volume": 1234567,
        "open": 1690.00,
        "previous_close": 1680.00,
        "timestamp": 1234567890,
        "exchange": "SSE"
    }
    """
    try:
        symbol_info = parse_symbol(symbol_str)
        ak_symbol = get_akshare_symbol(symbol_info)

        # Fetch realtime data based on market
        if symbol_info['asset_type'] == 'stock':
            if symbol_info['market'] in ['SSE', 'SZSE']:
                # A-Shares realtime from EastMoney
                df = ak.stock_zh_a_spot_em()
                row = df[df['代码'] == ak_symbol]
                if row.empty:
                    return {"error": f"No data for {symbol_str}", "symbol": symbol_str}

                row = row.iloc[0]
                current_price = float(row['最新价'])
                prev_close = float(row['昨收'])
                change = current_price - prev_close
                change_pct = (change / prev_close * 100) if prev_close else 0

                return {
                    "symbol": symbol_str,
                    "name": str(row['名称']),
                    "price": round(current_price, 2),
                    "change": round(change, 2),
                    "change_pct": round(change_pct, 2),
                    "high": round(float(row['最高']), 2),
                    "low": round(float(row['最低']), 2),
                    "volume": int(float(row['成交量'])) if pd.notna(row['成交量']) else 0,
                    "open": round(float(row['今开']), 2),
                    "previous_close": round(prev_close, 2),
                    "turnover": round(float(row['成交额']), 2) if pd.notna(row['成交额']) else 0,
                    "pe_ratio": round(float(row['市盈率-动态']), 2) if pd.notna(row['市盈率-动态']) else 0,
                    "market_cap": round(float(row['总市值']), 2) if pd.notna(row['总市值']) else 0,
                    "timestamp": int(datetime.now().timestamp()),
                    "exchange": symbol_info['market']
                }

            elif symbol_info['market'] == 'HKEX':
                # HK Stocks
                df = ak.stock_hk_spot_em()
                row = df[df['代码'] == ak_symbol]
                if row.empty:
                    return {"error": f"No data for {symbol_str}", "symbol": symbol_str}

                row = row.iloc[0]
                current_price = float(row['最新价'])
                prev_close = float(row['昨收'])
                change = current_price - prev_close
                change_pct = (change / prev_close * 100) if prev_close else 0

                return {
                    "symbol": symbol_str,
                    "name": str(row['名称']),
                    "price": round(current_price, 2),
                    "change": round(change, 2),
                    "change_pct": round(change_pct, 2),
                    "high": round(float(row['最高']), 2),
                    "low": round(float(row['最低']), 2),
                    "volume": int(float(row['成交量'])) if pd.notna(row['成交量']) else 0,
                    "open": round(float(row['今开']), 2),
                    "previous_close": round(prev_close, 2),
                    "timestamp": int(datetime.now().timestamp()),
                    "exchange": "HKEX"
                }

        elif symbol_info['asset_type'] == 'futures':
            # China Futures realtime
            df = ak.futures_zh_minute_sina(symbol=ak_symbol, period='1')
            if df.empty:
                return {"error": f"No futures data for {symbol_str}", "symbol": symbol_str}

            latest = df.iloc[-1]
            current_price = float(latest['close'])
            open_price = float(latest['open'])
            high = float(latest['high'])
            low = float(latest['low'])
            volume = int(latest['volume'])

            # For futures, calculate change from previous close (approximate)
            change = current_price - open_price
            change_pct = (change / open_price * 100) if open_price else 0

            return {
                "symbol": symbol_str,
                "name": ak_symbol,
                "price": round(current_price, 2),
                "change": round(change, 2),
                "change_pct": round(change_pct, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "volume": volume,
                "open": round(open_price, 2),
                "previous_close": round(open_price, 2),
                "timestamp": int(datetime.now().timestamp()),
                "exchange": symbol_info['exchange']
            }

        return {"error": f"Unsupported market type: {symbol_info['market']}", "symbol": symbol_str}

    except Exception as e:
        return {"error": str(e), "symbol": symbol_str}


def fetch_quotes_batch(symbols_list):
    """Fetch quotes for multiple symbols in batch

    Returns:
        List of quote dicts
    """
    results = []
    for symbol in symbols_list:
        quote = fetch_quote_single(symbol.strip())
        if 'error' not in quote:
            results.append(quote)
        else:
            print(f"Warning: {quote['error']}", file=sys.stderr)

    return results


def fetch_history(symbol_str, period='1y', interval='1d'):
    """Fetch historical OHLCV data

    Args:
        symbol_str: Symbol like "600519.SS"
        period: Time period - "1mo", "3mo", "6mo", "1y", "2y", "5y"
        interval: Data interval - "1d", "1wk", "1mo"

    Returns:
        List of HistoryPoint dicts with timestamp, open, high, low, close, volume
    """
    try:
        symbol_info = parse_symbol(symbol_str)
        ak_symbol = get_akshare_symbol(symbol_info)

        # Parse period to days
        period_map = {
            '1mo': 30, '3mo': 90, '6mo': 180,
            '1y': 365, '2y': 730, '5y': 1825
        }
        days = period_map.get(period, 365)

        # Parse interval
        interval_map = {'1d': 'daily', '1wk': 'weekly', '1mo': 'monthly'}
        adjust = interval_map.get(interval, 'daily')

        # Fetch historical data based on market
        if symbol_info['asset_type'] == 'stock':
            if symbol_info['market'] in ['SSE', 'SZSE']:
                # A-Shares historical data
                end_date = datetime.now().strftime('%Y%m%d')
                start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')

                df = ak.stock_zh_a_hist(
                    symbol=ak_symbol,
                    period=adjust,
                    start_date=start_date,
                    end_date=end_date,
                    adjust="qfq"  # Forward adjusted
                )

                if df.empty:
                    return []

                history = []
                for _, row in df.iterrows():
                    timestamp = int(pd.Timestamp(row['日期']).timestamp())
                    history.append({
                        "symbol": symbol_str,
                        "timestamp": timestamp,
                        "open": round(float(row['开盘']), 2),
                        "high": round(float(row['最高']), 2),
                        "low": round(float(row['最低']), 2),
                        "close": round(float(row['收盘']), 2),
                        "volume": int(row['成交量']),
                        "amount": round(float(row['成交额']), 2) if '成交额' in row else 0
                    })

                return history

        elif symbol_info['asset_type'] == 'futures':
            # Futures historical data
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')

            df = ak.futures_zh_daily_sina(symbol=ak_symbol)

            if df.empty:
                return []

            # Filter by date range
            df['date'] = pd.to_datetime(df['date'])
            mask = (df['date'] >= start_date) & (df['date'] <= end_date)
            df = df[mask]

            history = []
            for _, row in df.iterrows():
                timestamp = int(pd.Timestamp(row['date']).timestamp())
                history.append({
                    "symbol": symbol_str,
                    "timestamp": timestamp,
                    "open": round(float(row['open']), 2),
                    "high": round(float(row['high']), 2),
                    "low": round(float(row['low']), 2),
                    "close": round(float(row['close']), 2),
                    "volume": int(row['volume'])
                })

            return history

        return []

    except Exception as e:
        print(f"Error fetching history: {e}", file=sys.stderr)
        return []


def main():
    parser = argparse.ArgumentParser(description='China Market Data Interface')
    parser.add_argument('--symbols', type=str, help='Comma-separated symbols (e.g., 600519.SS,000001.SZ)')
    parser.add_argument('--symbol', type=str, help='Single symbol for history')
    parser.add_argument('--type', type=str, default='quote', choices=['quote', 'history'],
                        help='Data type: quote or history')
    parser.add_argument('--period', type=str, default='1y',
                        help='History period: 1mo, 3mo, 6mo, 1y, 2y, 5y')
    parser.add_argument('--interval', type=str, default='1d',
                        help='History interval: 1d, 1wk, 1mo')

    args = parser.parse_args()

    result = {"success": True, "data": [], "timestamp": int(datetime.now().timestamp())}

    try:
        if args.type == 'quote':
            if not args.symbols:
                result["success"] = False
                result["error"] = "--symbols required for quote type"
            else:
                symbols_list = [s.strip() for s in args.symbols.split(',')]
                quotes = fetch_quotes_batch(symbols_list)
                result["data"] = quotes
                result["count"] = len(quotes)

        elif args.type == 'history':
            if not args.symbol:
                result["success"] = False
                result["error"] = "--symbol required for history type"
            else:
                history = fetch_history(args.symbol, args.period, args.interval)
                result["data"] = history
                result["count"] = len(history)

    except Exception as e:
        result["success"] = False
        result["error"] = str(e)

    # Output JSON to stdout
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
