#!/usr/bin/env python3
"""
Test script for Backtrader Provider
Verifies basic functionality
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bt_engine.backtrader_provider import BacktraderProvider


def test_provider():
    """Test basic provider functionality"""
    print("=" * 60)
    print("Testing Backtrader Provider")
    print("=" * 60)

    provider = BacktraderProvider()

    # Test 1: Provider info
    print("\n1. Provider Information:")
    print(f"   Name: {provider.name}")
    print(f"   Version: {provider.version}")
    print(f"   Capabilities: {json.dumps(provider.capabilities, indent=2)}")

    # Test 2: Initialize
    print("\n2. Testing initialization...")
    result = provider.initialize({})
    print(f"   Result: {result}")

    # Test 3: Test connection
    print("\n3. Testing connection...")
    result = provider.test_connection()
    print(f"   Result: {result}")

    # Test 4: Get strategies
    print("\n4. Getting strategy catalog...")
    result = provider.get_strategies({})
    if result.get('success'):
        strategies = result['data']['strategies']
        print(f"   Found {len(strategies)} strategy categories")
        for category, items in strategies.items():
            print(f"   - {category}: {len(items)} strategies")
            for item in items[:2]:  # Show first 2
                print(f"     * {item['name']}")
    else:
        print(f"   Error: {result.get('error')}")

    # Test 5: Get indicators
    print("\n5. Getting indicator catalog...")
    result = provider.get_indicators({})
    if result.get('indicators'):
        indicators = result['indicators']
        print(f"   Found {len(indicators)} indicator categories")
        for category, items in indicators.items():
            print(f"   - {category}: {len(items)} indicators")
    else:
        print(f"   Error: {result}")

    # Test 6: Run simple backtest (if dependencies available)
    print("\n6. Testing simple backtest...")
    try:
        import backtrader
        import akshare
        print("   Dependencies available, running test...")

        request = {
            'strategy': {
                'type': 'ma_cross',
                'parameters': {
                    'fast_period': 5,
                    'slow_period': 20
                }
            },
            'startDate': '2023-01-01',
            'endDate': '2023-03-01',
            'initialCapital': 100000,
            'commission': 0.0003,
            'assets': [{'symbol': '600519.SS'}]
        }

        result = provider.run_backtest(request)
        if result.get('success'):
            data = result['data']
            perf = data['performance']
            print(f"   [OK] Backtest completed successfully")
            print(f"   - Total Return: {perf['totalReturn']:.2%}")
            print(f"   - Sharpe Ratio: {perf['sharpeRatio']:.3f}")
            print(f"   - Max Drawdown: {perf['maxDrawdown']:.2%}")
            print(f"   - Total Trades: {perf['totalTrades']}")
        else:
            print(f"   [FAIL] Backtest failed: {result.get('error')}")

    except ImportError as e:
        print(f"   [WARN] Skipping backtest test - missing dependency: {e}")
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)


if __name__ == '__main__':
    test_provider()
