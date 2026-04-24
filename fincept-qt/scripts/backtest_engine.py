#!/usr/bin/env python3
"""
Backtrader Integration Adapter for Fincept Terminal
Supports A-share, HK stocks, and China futures backtesting

Usage:
    python backtest_engine.py --symbol 600519.SS --start 2023-01-01 --end 2024-01-01 --strategy ma_cross
"""

import sys
import json
import argparse
from datetime import datetime

try:
    import backtrader as bt
    import akshare as ak
    import pandas as pd
except ImportError as e:
    print(json.dumps({
        "success": False,
        "error": f"Missing dependency: {e}. Install with: pip install backtrader akshare"
    }))
    sys.exit(1)


class AkShareDataFeed(bt.feeds.PandasData):
    """Custom data feed for AkShare historical data"""
    params = (
        ('datetime', None),
        ('open', '开盘'),
        ('high', '最高'),
        ('low', '最低'),
        ('close', '收盘'),
        ('volume', '成交量'),
        ('openinterest', -1),
    )


class MovingAverageCrossStrategy(bt.Strategy):
    """Simple Moving Average Crossover Strategy"""
    params = (
        ('fast_period', 5),
        ('slow_period', 20),
    )

    def __init__(self):
        self.fast_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.fast_period
        )
        self.slow_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.slow_period
        )
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)

    def next(self):
        if not self.position:
            if self.crossover > 0:
                self.buy()
        elif self.crossover < 0:
            self.sell()


class RSIStrategy(bt.Strategy):
    """RSI Mean Reversion Strategy"""
    params = (
        ('rsi_period', 14),
        ('rsi_lower', 30),
        ('rsi_upper', 70),
    )

    def __init__(self):
        self.rsi = bt.indicators.RSI(
            self.data.close, period=self.params.rsi_period
        )

    def next(self):
        if not self.position:
            if self.rsi < self.params.rsi_lower:
                self.buy()
        elif self.rsi > self.params.rsi_upper:
            self.sell()


class BollingerBandsStrategy(bt.Strategy):
    """Bollinger Bands Breakout Strategy"""
    params = (
        ('bb_period', 20),
        ('bb_devfactor', 2.0),
    )

    def __init__(self):
        self.bb = bt.indicators.BollingerBands(
            self.data.close,
            period=self.params.bb_period,
            devfactor=self.params.bb_devfactor
        )

    def next(self):
        if not self.position:
            if self.data.close[0] < self.bb.lines.bot[0]:
                self.buy()
        elif self.data.close[0] > self.bb.lines.top[0]:
            self.sell()


def fetch_china_stock_data(symbol, start_date, end_date):
    """Fetch historical data from AkShare"""
    try:
        # Parse symbol
        if '.SS' in symbol or '.SZ' in symbol:
            code = symbol.split('.')[0]
        else:
            code = symbol

        # Fetch data
        df = ak.stock_zh_a_hist(
            symbol=code,
            period="daily",
            start_date=start_date.replace('-', ''),
            end_date=end_date.replace('-', ''),
            adjust="qfq"  # Forward adjusted
        )

        if df.empty:
            return None

        # Rename columns to match Backtrader expectations
        df.rename(columns={
            '日期': 'date',
            '开盘': 'open',
            '最高': 'high',
            '最低': 'low',
            '收盘': 'close',
            '成交量': 'volume',
            '成交额': 'turnover'
        }, inplace=True)

        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        # Convert volume to float (AkShare returns string with commas)
        df['volume'] = df['volume'].astype(str).str.replace(',', '').astype(float)
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)

        return df

    except Exception as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        return None


def run_backtest(symbol, start_date, end_date, strategy_name, initial_cash=100000.0):
    """Run backtest with specified strategy"""

    # Fetch data
    print(f"Fetching data for {symbol}...", file=sys.stderr)
    df = fetch_china_stock_data(symbol, start_date, end_date)

    if df is None or df.empty:
        return {"success": False, "error": "No data available"}

    print(f"Data fetched: {len(df)} bars", file=sys.stderr)

    # Create Cerebro engine
    cerebro = bt.Cerebro()

    # Add data feed
    data = AkShareDataFeed(dataname=df)
    cerebro.adddata(data)

    # Add strategy
    if strategy_name == "ma_cross":
        cerebro.addstrategy(MovingAverageCrossStrategy)
    elif strategy_name == "rsi":
        cerebro.addstrategy(RSIStrategy)
    elif strategy_name == "bollinger":
        cerebro.addstrategy(BollingerBandsStrategy)
    else:
        return {"success": False, "error": f"Unknown strategy: {strategy_name}"}

    # Set initial cash
    cerebro.broker.setcash(initial_cash)

    # Set commission (A-share typical: 0.03%)
    cerebro.broker.setcommission(commission=0.0003)

    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

    # Run backtest
    print("Running backtest...", file=sys.stderr)
    results = cerebro.run()
    strategy = results[0]

    # Get final portfolio value
    final_value = cerebro.broker.getvalue()

    # Extract analyzer results
    sharpe_ratio = strategy.analyzers.sharpe.get_analysis()
    drawdown = strategy.analyzers.drawdown.get_analysis()
    trades = strategy.analyzers.trades.get_analysis()
    returns = strategy.analyzers.returns.get_analysis()

    # Build result
    result = {
        "success": True,
        "symbol": symbol,
        "period": f"{start_date} to {end_date}",
        "initial_cash": initial_cash,
        "final_value": round(final_value, 2),
        "total_return": round((final_value - initial_cash) / initial_cash * 100, 2),
        "sharpe_ratio": round(sharpe_ratio.get('sharperatio', 0), 3),
        "max_drawdown": round(drawdown.get('max', {}).get('drawdown', 0), 2),
        "total_trades": trades.get('total', {}).get('total', 0),
        "winning_trades": trades.get('won', {}).get('total', 0),
        "losing_trades": trades.get('lost', {}).get('total', 0),
        "win_rate": round(
            trades.get('won', {}).get('total', 0) / max(trades.get('total', {}).get('total', 1), 1) * 100,
            2
        ),
        "annualized_return": round(returns.get('rnorm', 0) * 100, 2),
    }

    return result


def main():
    parser = argparse.ArgumentParser(description='China Stock Backtest Engine')

    parser.add_argument('--symbol', required=True, help='Stock symbol (e.g., 600519.SS)')
    parser.add_argument('--start', required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', required=True, help='End date (YYYY-MM-DD)')
    parser.add_argument('--strategy', default='ma_cross',
                        choices=['ma_cross', 'rsi', 'bollinger'],
                        help='Strategy to use')
    parser.add_argument('--cash', type=float, default=100000.0, help='Initial cash')

    args = parser.parse_args()

    try:
        result = run_backtest(args.symbol, args.start, args.end, args.strategy, args.cash)
        print(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": str(e)
        }))
        sys.exit(1)


if __name__ == '__main__':
    main()
