#!/usr/bin/env python3
"""
Debug script for Backtrader Provider
Easy to modify and test different scenarios
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bt_engine.backtrader_provider import BacktraderProvider


def debug_basic_test():
    """Basic functionality test"""
    print("=" * 70)
    print("BASIC FUNCTIONALITY TEST")
    print("=" * 70)

    provider = BacktraderProvider()

    # Test connection
    print("\n[1] Testing connection...")
    result = provider.test_connection()
    print(f"    Status: {result['success']}")
    print(f"    Message: {result['message']}")

    # Get strategies
    print("\n[2] Available strategies:")
    result = provider.get_strategies({})
    if result.get('success'):
        strategies = result['data']['strategies']
        for category, items in strategies.items():
            print(f"\n    {category.upper()}:")
            for item in items:
                print(f"      - {item['id']}: {item['name']}")
                print(f"        {item['description']}")

    return provider


def debug_single_backtest(provider=None):
    """Test a single backtest with custom parameters"""
    print("\n" + "=" * 70)
    print("SINGLE BACKTEST TEST")
    print("=" * 70)

    if provider is None:
        provider = BacktraderProvider()

    # Configuration - MODIFY THESE PARAMETERS
    config = {
        'strategy': {
            'type': 'ma_cross',  # Try: 'rsi', 'macd', 'bollinger', 'ema_cross'
            'parameters': {
                'fast_period': 5,
                'slow_period': 20,
            }
        },
        'startDate': '2023-01-01',
        'endDate': '2023-06-01',
        'initialCapital': 100000,
        'commission': 0.0003,  # 0.03% typical for A-shares
        'assets': [
            {'symbol': '600519.SS'}  # Kweichow Moutai
            # Try: '000001.SZ' (Ping An), '600036.SS' (China Merchants Bank)
        ]
    }

    print(f"\nStrategy: {config['strategy']['type']}")
    print(f"Symbol: {config['assets'][0]['symbol']}")
    print(f"Period: {config['startDate']} to {config['endDate']}")
    print(f"Initial Capital: {config['initialCapital']:,.0f}")
    print("-" * 70)

    try:
        result = provider.run_backtest(config)

        if result.get('success'):
            data = result['data']
            perf = data['performance']
            stats = data['statistics']

            print("\n[RESULTS]")
            print(f"  Final Capital:    {stats['finalCapital']:>12,.2f}")
            print(f"  Total Return:     {perf['totalReturn']:>12.2%}")
            print(f"  Annualized Return:{perf['annualizedReturn']:>12.2%}")
            print(f"  Sharpe Ratio:     {perf['sharpeRatio']:>12.3f}")
            print(f"  Sortino Ratio:    {perf['sortinoRatio']:>12.3f}")
            print(f"  Max Drawdown:     {perf['maxDrawdown']:>12.2%}")
            print(f"  Win Rate:         {perf['winRate']:>12.2%}")
            print(f"  Total Trades:     {perf['totalTrades']:>12d}")
            print(f"  Winning Trades:   {perf['winningTrades']:>12d}")
            print(f"  Losing Trades:    {perf['losingTrades']:>12d}")

            if data.get('using_synthetic_data'):
                print("\n  [WARNING] Using synthetic data!")
                print(f"  {data.get('synthetic_data_warning', '')}")
        else:
            print(f"\n[ERROR] Backtest failed:")
            print(f"  {result.get('error')}")
            if result.get('traceback'):
                print(f"\nTraceback:\n{result['traceback']}")

    except Exception as e:
        print(f"\n[EXCEPTION] {e}")
        import traceback
        traceback.print_exc()


def debug_optimization(provider=None):
    """Test parameter optimization"""
    print("\n" + "=" * 70)
    print("PARAMETER OPTIMIZATION TEST")
    print("=" * 70)

    if provider is None:
        provider = BacktraderProvider()

    config = {
        'strategy': {
            'type': 'ma_cross',
        },
        'startDate': '2023-01-01',
        'endDate': '2023-04-01',
        'initialCapital': 100000,
        'objective': 'sharpe',  # Optimize for Sharpe ratio
        'method': 'grid',  # or 'random'
        'maxIterations': 10,
        'parameters': {
            'fast_period': {'min': 3, 'max': 10, 'step': 2},
            'slow_period': {'min': 15, 'max': 30, 'step': 5},
        },
        'assets': [{'symbol': '600519.SS'}]
    }

    print(f"\nOptimizing: {config['strategy']['type']}")
    print(f"Method: {config['method']}")
    print(f"Iterations: {config['maxIterations']}")
    print(f"Objective: {config['objective']}")
    print("-" * 70)

    try:
        result = provider.optimize(config)

        if result.get('success'):
            data = result['data']
            print(f"\n[OPTIMIZATION RESULTS]")
            print(f"  Best Parameters: {data['bestParameters']}")
            print(f"  Best Score: {data['bestScore']:.3f}")
            print(f"  Total Iterations: {data['iterations']}")

            print(f"\n  Top 5 Results:")
            sorted_results = sorted(data['allResults'], key=lambda x: x['score'], reverse=True)
            for i, res in enumerate(sorted_results[:5], 1):
                print(f"    {i}. Params: {res['parameters']}, Score: {res['score']:.3f}")
        else:
            print(f"\n[ERROR] Optimization failed: {result.get('error')}")

    except Exception as e:
        print(f"\n[EXCEPTION] {e}")
        import traceback
        traceback.print_exc()


def debug_walk_forward(provider=None):
    """Test walk-forward analysis"""
    print("\n" + "=" * 70)
    print("WALK-FORWARD ANALYSIS TEST")
    print("=" * 70)

    if provider is None:
        provider = BacktraderProvider()

    config = {
        'strategy': {
            'type': 'ma_cross',
            'parameters': {'fast_period': 5, 'slow_period': 20}
        },
        'startDate': '2023-01-01',
        'endDate': '2023-12-01',
        'initialCapital': 100000,
        'nSplits': 4,
        'trainRatio': 0.7,
        'assets': [{'symbol': '600519.SS'}]
    }

    print(f"\nWalk-forward analysis: {config['nSplits']} splits")
    print("-" * 70)

    try:
        result = provider.walk_forward(config)

        if result.get('success'):
            data = result['data']
            print(f"\n[WALK-FORWARD RESULTS]")
            print(f"  Average Return: {data['summary']['averageReturn']:.2%}")
            print(f"  Average Sharpe: {data['summary']['averageSharpe']:.3f}")

            print(f"\n  Individual Splits:")
            for split in data['splits']:
                print(f"    Split {split['split']}: "
                      f"Return={split['totalReturn']:.2%}, "
                      f"Sharpe={split['sharpeRatio']:.3f}, "
                      f"MaxDD={split['maxDrawdown']:.2%}")
        else:
            print(f"\n[ERROR] Walk-forward failed: {result.get('error')}")

    except Exception as e:
        print(f"\n[EXCEPTION] {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main debug entry point"""
    print("\nBacktrader Provider Debug Tool")
    print("Select test to run:")
    print("  1. Basic functionality test")
    print("  2. Single backtest test")
    print("  3. Parameter optimization test")
    print("  4. Walk-forward analysis test")
    print("  5. Run all tests")
    print()

    choice = input("Enter choice (1-5, default=2): ").strip() or '2'

    provider = None

    if choice == '1':
        provider = debug_basic_test()
    elif choice == '2':
        provider = debug_basic_test()
        debug_single_backtest(provider)
    elif choice == '3':
        provider = debug_basic_test()
        debug_optimization(provider)
    elif choice == '4':
        provider = debug_basic_test()
        debug_walk_forward(provider)
    elif choice == '5':
        provider = debug_basic_test()
        debug_single_backtest(provider)
        debug_optimization(provider)
        debug_walk_forward(provider)
    else:
        print("Invalid choice")
        return

    print("\n" + "=" * 70)
    print("DEBUG COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
