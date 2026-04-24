#!/usr/bin/env python3
"""
Test script for China Market Data Interface
Validates: A-Shares, HK Stocks, Futures, ETFs data fetching
"""

import subprocess
import json
import sys


def test_symbol(symbol, data_type="quote"):
    """Test a single symbol"""
    cmd = [
        sys.executable, "china_market_data.py",
        "--type", data_type
    ]

    if data_type == "quote":
        cmd.extend(["--symbols", symbol])
    else:
        cmd.extend(["--symbol", symbol, "--period", "1mo", "--interval", "1d"])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"[ERROR] {symbol}: Process failed")
            print(f"   Error: {result.stderr}")
            return False

        data = json.loads(result.stdout)
        if not data.get("success"):
            print(f"[ERROR] {symbol}: API returned error")
            print(f"   Error: {data.get('error')}")
            return False

        if data_type == "quote":
            quotes = data.get("data", [])
            if quotes:
                q = quotes[0]
                print(f"[OK] {symbol}: {q.get('name', 'N/A')} - Price:{q.get('price', 0):.2f} Change:{q.get('change_pct', 0):+.2f}%")
                return True
            else:
                print(f"[WARN] {symbol}: No data returned")
                return False
        else:
            history = data.get("data", [])
            if history:
                print(f"[OK] {symbol}: {len(history)} history records fetched")
                return True
            else:
                print(f"[WARN] {symbol}: No history data")
                return False

    except Exception as e:
        print(f"[ERROR] {symbol}: Exception - {e}")
        return False


def main():
    print("=" * 70)
    print("China Market Data Interface - Test Suite")
    print("=" * 70)

    # Test A-Shares
    print("\n[TEST] Testing A-Shares (Shanghai & Shenzhen)...")
    a_shares = [
        "600519.SS",  # Kweichow Moutai
        "000001.SZ",  # Ping An Bank
        "300750.SZ",  # CATL
    ]
    for sym in a_shares:
        test_symbol(sym)

    # Test HK Stocks
    print("\n[TEST] Testing Hong Kong Stocks...")
    hk_stocks = [
        "0700.HK",    # Tencent
        "9988.HK",    # Alibaba
    ]
    for sym in hk_stocks:
        test_symbol(sym)

    # Test Futures
    print("\n[TEST] Testing China Futures...")
    futures = [
        "rb2405.SHF",  # Rebar
        "IF2405.CFX",  # CSI 300 Index Future
    ]
    for sym in futures:
        test_symbol(sym)

    # Test ETFs
    print("\n[TEST] Testing China ETFs...")
    etfs = [
        "510300.SS",  # CSI 300 ETF
    ]
    for sym in etfs:
        test_symbol(sym)

    # Test historical data
    print("\n[TEST] Testing Historical Data...")
    test_symbol("600519.SS", data_type="history")

    # Test batch fetch
    print("\n[TEST] Testing Batch Fetch (multiple symbols)...")
    batch_symbols = "600519.SS,000001.SZ,300750.SZ"
    test_symbol(batch_symbols)

    print("\n" + "=" * 70)
    print("Test Complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
