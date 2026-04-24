#!/usr/bin/env python3
"""
Test and demo for Risk Monitoring System
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bt_engine.br_risk_monitor import RiskMonitor, AlertLevel, create_risk_monitor
from bt_engine.br_portfolio import create_china_portfolio
import pandas as pd
import numpy as np


def test_risk_monitor():
    """Test risk monitoring system"""
    print("=" * 70)
    print("RISK MONITORING SYSTEM TEST")
    print("=" * 70)

    # Create risk monitor with custom thresholds
    config = {
        'max_drawdown': 0.08,       # 8% max drawdown
        'max_position_weight': 0.25, # 25% max position
        'max_sector_weight': 0.40,   # 40% max sector
        'max_portfolio_vol': 0.25,   # 25% max volatility
        'var_confidence': 0.95,      # 95% VaR
        'max_correlation': 0.75,     # 0.75 max correlation
        'stop_loss_levels': {
            'warning': -0.05,
            'critical': -0.10,
            'emergency': -0.15,
        }
    }

    print("\n[1] Creating risk monitor...")
    monitor = create_risk_monitor(config)
    print(f"    Configuration loaded")
    print(f"    Max Drawdown: {config['max_drawdown']:.0%}")
    print(f"    Max Position: {config['max_position_weight']:.0%}")
    print(f"    Stop Loss Levels: {', '.join(f'{k}={v:.0%}' for k, v in config['stop_loss_levels'].items())}")

    # Create sample portfolio
    print("\n[2] Creating test portfolio...")
    symbols = ['600519.SS', '000001.SZ', '600036.SS', '000858.SZ', '600276.SS']
    portfolio = create_china_portfolio(1000000.0, symbols)

    sector_map = {
        '600519.SS': 'Consumer Staples',
        '000001.SZ': 'Financials',
        '600036.SS': 'Financials',
        '000858.SZ': 'Consumer Staples',
        '600276.SS': 'Healthcare',
    }
    portfolio.set_sector_map(sector_map)

    # Generate price data with some stress scenarios
    print("\n[3] Generating market data (with stress scenarios)...")
    dates = pd.bdate_range(start='2023-01-01', periods=100)
    n_days = len(dates)

    price_data = {}
    np.random.seed(42)

    for sym in symbols:
        # Normal returns with occasional spikes
        returns = np.random.normal(0.0005, 0.02, n_days)

        # Add some stress events
        if sym == '600519.SS':
            returns[80] = -0.08  # Sharp drop
            returns[85] = -0.06
        elif sym == '000001.SZ':
            returns[70] = 0.10   # Spike up
            returns[71] = -0.07  # Then crash

        prices = 100 * np.cumprod(1 + returns)
        price_data[sym] = prices

    prices_df = pd.DataFrame(price_data, index=dates)
    returns_df = prices_df.pct_change().dropna()

    print(f"    Generated {n_days} days of data for {len(symbols)} assets")
    print(f"    Included stress scenarios (sharp moves)")

    # Simulate portfolio with positions
    print("\n[4] Setting up portfolio positions...")

    # Manually set some positions to trigger alerts
    portfolio.positions['600519.SS'].update({
        'quantity': 2500,
        'avg_cost': 180.0,
        'current_price': prices_df['600519.SS'].iloc[-1],
        'current_weight': 0.30,  # Exceeds 25% limit
        'market_value': 2500 * prices_df['600519.SS'].iloc[-1],
    })

    portfolio.positions['000001.SZ'].update({
        'quantity': 1500,
        'avg_cost': 150.0,
        'current_price': prices_df['000001.SZ'].iloc[-1],
        'current_weight': 0.20,
        'market_value': 1500 * prices_df['000001.SZ'].iloc[-1],
    })

    # Calculate portfolio values over time
    portfolio_values = []
    for i in range(len(dates)):
        value = 1000000  # Start with 1M
        for sym, pos in portfolio.positions.items():
            if sym in prices_df.columns and pos['quantity'] > 0:
                value += pos['quantity'] * prices_df[sym].iloc[i]
        portfolio_values.append(value)

    portfolio_values_series = pd.Series(portfolio_values, index=dates)

    # Add drawdown scenario
    portfolio_values_series.iloc[80:] *= 0.90  # 10% drawdown

    # Prepare portfolio data for risk check
    portfolio_data = {
        'portfolio_value': portfolio_values_series.iloc[-1],
        'portfolio_values': portfolio_values_series,
        'positions': {sym: pos for sym, pos in portfolio.positions.items() if pos['quantity'] > 0},
        'sector_weights': {
            'Consumer Staples': 0.45,  # Exceeds 40% limit
            'Financials': 0.35,
            'Healthcare': 0.20,
        }
    }

    # Run risk checks
    print("\n[5] Running comprehensive risk checks...")
    print("-" * 70)

    alerts = monitor.check_portfolio_risks(portfolio_data, prices_df, returns_df)

    if alerts:
        print(f"\n    Found {len(alerts)} risk alert(s):\n")
        for i, alert in enumerate(alerts, 1):
            level_icon = {
                'INFO': '[INFO]',
                'WARNING': '[WARN]',
                'CRITICAL': '[CRIT]',
                'EMERGENCY': '[EMERG]',
            }.get(alert.level.value, '[----]')

            print(f"    {i}. {level_icon} {alert.alert_type.value.upper()}")
            print(f"       {alert.message}")
            if alert.symbol:
                print(f"       Symbol: {alert.symbol}")
            print(f"       Current: {alert.current_value:.2%}, Threshold: {alert.threshold:.2%}")
            print()
    else:
        print("\n    No risk alerts triggered - portfolio is within limits")

    # Get risk summary
    print("\n[6] Risk Summary:")
    summary = monitor.get_risk_summary()
    print(f"    Status: {summary['status']}")
    print(f"    Risk Level: {summary['risk_level']}")
    print(f"    Total Alerts: {summary['alert_count']}")

    if summary.get('by_level'):
        print(f"    By Level:")
        for level, count in summary['by_level'].items():
            print(f"      {level}: {count}")

    # Check individual position risks
    print("\n[7] Checking individual position risks...")
    positions_list = [pos for pos in portfolio.positions.values() if pos['quantity'] > 0]
    position_alerts = monitor.check_position_risks(positions_list, prices_df)

    if position_alerts:
        print(f"    Found {len(position_alerts)} position alert(s):")
        for alert in position_alerts:
            print(f"      - [{alert.level.value}] {alert.message}")
    else:
        print("    No position-level alerts")

    # Alert history
    print("\n[8] Alert History:")
    history = monitor.get_alert_history(limit=5)
    print(f"    Recent alerts: {len(history)}")
    for h in history[-3:]:
        print(f"      [{h['timestamp']}] {h['type']}: {h['message'][:50]}...")

    print("\n" + "=" * 70)
    print("RISK MONITOR TEST COMPLETE")
    print("=" * 70)

    return monitor, alerts


def demonstrate_alert_scenarios():
    """Demonstrate different alert scenarios"""
    print("\n" + "=" * 70)
    print("ALERT SCENARIOS DEMONSTRATION")
    print("=" * 70)

    monitor = create_risk_monitor({
        'max_drawdown': 0.05,
        'max_position_weight': 0.20,
    })

    scenarios = [
        {
            'name': 'Normal Market',
            'portfolio_data': {
                'portfolio_value': 1000000,
                'portfolio_values': pd.Series([1000000, 1005000, 1002000]),
                'positions': {},
                'sector_weights': {'Tech': 0.30},
            },
            'returns': pd.DataFrame({'A': [0.001, 0.002, -0.001]}),
        },
        {
            'name': 'High Drawdown',
            'portfolio_data': {
                'portfolio_value': 900000,
                'portfolio_values': pd.Series([1000000, 950000, 900000, 890000]),
                'positions': {},
                'sector_weights': {},
            },
            'returns': pd.DataFrame({'A': [-0.05, -0.03, -0.02]}),
        },
        {
            'name': 'Position Concentration',
            'portfolio_data': {
                'portfolio_value': 1000000,
                'portfolio_values': pd.Series([1000000, 1002000]),
                'positions': {
                    'STOCK_A': {'current_weight': 0.35},  # Exceeds 20%
                },
                'sector_weights': {},
            },
            'returns': pd.DataFrame({'STOCK_A': [0.01, 0.02]}),
        },
    ]

    for scenario in scenarios:
        print(f"\n    Scenario: {scenario['name']}")
        print("    " + "-" * 60)

        alerts = monitor.check_portfolio_risks(
            scenario['portfolio_data'],
            pd.DataFrame(),  # Not used in these simple tests
            scenario['returns']
        )

        if alerts:
            for alert in alerts:
                print(f"      [{alert.level.value}] {alert.message}")
        else:
            print("      No alerts - within normal parameters")

    print("\n" + "=" * 70)
    print("SCENARIOS DEMONSTRATION COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    monitor, alerts = test_risk_monitor()
    demonstrate_alert_scenarios()

    print("\n\nSUMMARY:")
    print(f"  - Risk Monitor: Operational")
    print(f"  - Alert Types: {[a.value for a in type(alerts[0]).__dict__.get('_alert_type_', [])] if alerts else 'None triggered'}")
    print(f"  - Ready for integration with live trading systems")
