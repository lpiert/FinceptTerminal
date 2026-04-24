#!/usr/bin/env python3
"""
Test and demo for China Asset Portfolio Manager
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bt_engine.br_portfolio import ChinaAssetPortfolio, create_china_portfolio
import pandas as pd
import numpy as np


def test_basic_portfolio():
    """Test basic portfolio functionality"""
    print("=" * 70)
    print("CHINA ASSET PORTFOLIO TEST")
    print("=" * 70)

    # Create portfolio with sample A-share stocks
    symbols = [
        '600519.SS',  # Kweichow Moutai (Consumer)
        '000001.SZ',  # Ping An Bank (Financial)
        '600036.SS',  # China Merchants Bank (Financial)
        '000858.SZ',  # Wuliangye (Consumer)
        '600276.SS',  # Hengrui Medicine (Healthcare)
    ]

    # Sector classification
    sector_map = {
        '600519.SS': 'Consumer Staples',
        '000001.SZ': 'Financials',
        '600036.SS': 'Financials',
        '000858.SZ': 'Consumer Staples',
        '600276.SS': 'Healthcare',
    }

    print("\n[1] Creating portfolio...")
    portfolio = create_china_portfolio(
        initial_capital=1000000.0,
        symbols=symbols,
        weighting_scheme='equal'
    )
    portfolio.set_sector_map(sector_map)
    print(f"    Initial Capital: CNY{portfolio.initial_capital:,.0f}")
    print(f"    Number of Assets: {len(portfolio.positions)}")

    # Generate synthetic price data
    print("\n[2] Generating sample price data...")
    dates = pd.bdate_range(start='2023-01-01', end='2023-06-01')
    n_days = len(dates)

    price_data = {}
    np.random.seed(42)
    for sym in symbols:
        # Random walk with drift
        daily_returns = np.random.normal(0.0005, 0.02, n_days)
        prices = 100 * np.cumprod(1 + daily_returns)
        price_data[sym] = prices

    prices_df = pd.DataFrame(price_data, index=dates)
    returns_df = prices_df.pct_change()

    print(f"    Data points: {n_days} days")
    print(f"    Date range: {dates[0].strftime('%Y-%m-%d')} to {dates[-1].strftime('%Y-%m-%d')}")

    # Test different weighting schemes
    print("\n[3] Testing weighting schemes...")

    # Equal weight
    weights_equal = portfolio.calculate_weights_equal()
    print(f"\n    Equal Weight:")
    for sym, w in weights_equal.items():
        print(f"      {sym}: {w:.1%}")

    # Inverse volatility
    weights_inv_vol = portfolio.calculate_weights_inverse_vol(returns_df)
    print(f"\n    Inverse Volatility:")
    for sym, w in weights_inv_vol.items():
        print(f"      {sym}: {w:.1%}")

    # Risk parity
    weights_risk_parity = portfolio.calculate_weights_risk_parity(returns_df)
    print(f"\n    Risk Parity:")
    for sym, w in weights_risk_parity.items():
        print(f"      {sym}: {w:.1%}")

    # Momentum
    weights_momentum = portfolio.calculate_weights_momentum(returns_df, top_n=3)
    print(f"\n    Momentum (Top 3):")
    for sym, w in weights_momentum.items():
        if w > 0:
            print(f"      {sym}: {w:.1%}")

    # Rebalance portfolio
    print("\n[4] Rebalancing portfolio (using equal weights)...")
    result = portfolio.rebalance(prices_df, weights_equal, dates[-1].strftime('%Y-%m-%d'))
    print(f"    Portfolio Value: CNY{result['portfolio_value']:,.2f}")
    print(f"    Number of Trades: {result['num_trades']}")

    if result['trades']:
        print(f"\n    Sample Trades (first 3):")
        for trade in result['trades'][:3]:
            print(f"      {trade['action'].upper()} {trade['symbol']}: "
                  f"{trade['quantity']} shares @ CNY{trade['price']:.2f}")

    # Get performance metrics
    print("\n[5] Performance Metrics:")
    metrics = portfolio.get_performance_metrics(prices_df)
    if metrics:
        print(f"    Total Return:     {metrics['total_return']:>10.2%}")
        print(f"    Annual Return:    {metrics['annual_return']:>10.2%}")
        print(f"    Volatility:       {metrics['volatility']:>10.2%}")
        print(f"    Sharpe Ratio:     {metrics['sharpe_ratio']:>10.3f}")
        print(f"    Max Drawdown:     {metrics['max_drawdown']:>10.2%}")
        print(f"    Alpha:            {metrics['alpha']:>10.3f}")
        print(f"    Beta:             {metrics['beta']:>10.3f}")

    # Position summary
    print("\n[6] Position Summary:")
    positions = portfolio.get_position_summary()
    for pos in positions:
        print(f"    {pos['symbol']}: "
              f"Weight={pos['weight']:.1%}, "
              f"P&L=CNY{pos['pnl']:,.0f} ({pos['pnl_pct']:.1%})")

    # Sector allocation
    print("\n[7] Sector Allocation:")
    sectors = portfolio.get_sector_allocation()
    for sector, weight in sectors.items():
        print(f"    {sector}: {weight:.1%}")

    print("\n" + "=" * 70)
    print("PORTFOLIO TEST COMPLETE")
    print("=" * 70)

    return portfolio


def test_rebalancing_strategies():
    """Test different rebalancing strategies"""
    print("\n" + "=" * 70)
    print("REBALANCING STRATEGY TEST")
    print("=" * 70)

    symbols = ['600519.SS', '000001.SZ', '600036.SS']
    portfolio = create_china_portfolio(1000000.0, symbols)

    # Generate price data
    dates = pd.bdate_range(start='2023-01-01', periods=100)
    price_data = {}
    np.random.seed(123)
    for sym in symbols:
        daily_returns = np.random.normal(0.0005, 0.015, 100)
        prices = 100 * np.cumprod(1 + daily_returns)
        price_data[sym] = prices

    prices_df = pd.DataFrame(price_data, index=dates)

    # Monthly rebalancing simulation
    print("\nSimulating monthly rebalancing...")
    rebalance_dates = dates[::20]  # Every 20 trading days

    for date in rebalance_dates:
        mask = prices_df.index <= date
        subset_prices = prices_df[mask]

        if len(subset_prices) < 10:
            continue

        weights = portfolio.calculate_weights_equal()
        result = portfolio.rebalance(
            subset_prices,
            weights,
            date.strftime('%Y-%m-%d')
        )

        print(f"  {date.strftime('%Y-%m-%d')}: "
              f"Value=CNY{result['portfolio_value']:,.0f}, "
              f"Trades={result['num_trades']}")

    print("\nRebalancing test complete!")


if __name__ == '__main__':
    test_basic_portfolio()
    test_rebalancing_strategies()
