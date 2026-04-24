"""
Backtrader Strategies Module - Built-in trading strategies

Provides various pre-built strategies for backtesting:
- Moving Average Crossover
- RSI Mean Reversion
- Bollinger Bands Breakout
- MACD Signal
- Dual Moving Average with Stop Loss
- Momentum Strategy
"""

import backtrader as bt


class MovingAverageCrossStrategy(bt.Strategy):
    """
    Simple Moving Average Crossover Strategy

    Buy when fast MA crosses above slow MA
    Sell when fast MA crosses below slow MA
    """
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


class EMACrossStrategy(bt.Strategy):
    """
    Exponential Moving Average Crossover Strategy

    Similar to MA crossover but uses EMA for faster response
    """
    params = (
        ('fast_period', 12),
        ('slow_period', 26),
    )

    def __init__(self):
        self.fast_ema = bt.indicators.ExponentialMovingAverage(
            self.data.close, period=self.params.fast_period
        )
        self.slow_ema = bt.indicators.ExponentialMovingAverage(
            self.data.close, period=self.params.slow_period
        )
        self.crossover = bt.indicators.CrossOver(self.fast_ema, self.slow_ema)

    def next(self):
        if not self.position:
            if self.crossover > 0:
                self.buy()
        elif self.crossover < 0:
            self.sell()


class RSIStrategy(bt.Strategy):
    """
    RSI Mean Reversion Strategy

    Buy when RSI is oversold (<30)
    Sell when RSI is overbought (>70)
    """
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
    """
    Bollinger Bands Breakout Strategy

    Buy when price touches lower band
    Sell when price touches upper band
    """
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


class MACDStrategy(bt.Strategy):
    """
    MACD Signal Line Crossover Strategy

    Buy when MACD line crosses above signal line
    Sell when MACD line crosses below signal line
    """
    params = (
        ('fast_period', 12),
        ('slow_period', 26),
        ('signal_period', 9),
    )

    def __init__(self):
        self.macd = bt.indicators.MACD(
            self.data.close,
            period_me1=self.params.fast_period,
            period_me2=self.params.slow_period,
            period_signal=self.params.signal_period
        )
        self.crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)

    def next(self):
        if not self.position:
            if self.crossover > 0:
                self.buy()
        elif self.crossover < 0:
            self.sell()


class DualMAStrategyWithStop(bt.Strategy):
    """
    Dual Moving Average Strategy with Stop Loss and Take Profit

    Features:
    - Entry on MA crossover
    - Stop loss at specified percentage
    - Take profit at specified percentage
    """
    params = (
        ('fast_period', 10),
        ('slow_period', 30),
        ('stop_loss_pct', 5.0),
        ('take_profit_pct', 10.0),
    )

    def __init__(self):
        self.fast_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.fast_period
        )
        self.slow_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.slow_period
        )
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)
        self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.entry_price = order.executed.price
            elif order.issell():
                self.entry_price = None

    def next(self):
        # Check stop loss and take profit
        if self.position and self.entry_price:
            current_price = self.data.close[0]
            pnl_pct = (current_price - self.entry_price) / self.entry_price * 100

            if pnl_pct <= -self.params.stop_loss_pct:
                self.close()  # Stop loss hit
                return
            elif pnl_pct >= self.params.take_profit_pct:
                self.close()  # Take profit hit
                return

        # Entry/exit signals
        if not self.position:
            if self.crossover > 0:
                self.buy()
        elif self.crossover < 0:
            self.close()


class MomentumStrategy(bt.Strategy):
    """
    Price Momentum Strategy

    Buy when price has positive momentum over lookback period
    Sell when momentum turns negative
    """
    params = (
        ('momentum_period', 20),
    )

    def __init__(self):
        self.momentum = bt.indicators.RateOfChange(
            self.data.close, period=self.params.momentum_period
        )

    def next(self):
        if not self.position:
            if self.momentum > 0:
                self.buy()
        elif self.momentum < 0:
            self.sell()


# Strategy catalog for UI display
STRATEGY_CATALOG = {
    'trend_following': [
        {
            'id': 'ma_cross',
            'name': 'Moving Average Crossover',
            'description': 'Buy when fast MA crosses above slow MA',
            'parameters': {
                'fast_period': {'type': 'int', 'default': 5, 'min': 2, 'max': 50},
                'slow_period': {'type': 'int', 'default': 20, 'min': 5, 'max': 200},
            }
        },
        {
            'id': 'ema_cross',
            'name': 'EMA Crossover',
            'description': 'Exponential MA crossover for faster signals',
            'parameters': {
                'fast_period': {'type': 'int', 'default': 12, 'min': 2, 'max': 50},
                'slow_period': {'type': 'int', 'default': 26, 'min': 5, 'max': 200},
            }
        },
        {
            'id': 'macd',
            'name': 'MACD Signal',
            'description': 'MACD line crossover strategy',
            'parameters': {
                'fast_period': {'type': 'int', 'default': 12, 'min': 5, 'max': 30},
                'slow_period': {'type': 'int', 'default': 26, 'min': 10, 'max': 50},
                'signal_period': {'type': 'int', 'default': 9, 'min': 3, 'max': 20},
            }
        },
        {
            'id': 'momentum',
            'name': 'Momentum Strategy',
            'description': 'Trade based on price momentum',
            'parameters': {
                'momentum_period': {'type': 'int', 'default': 20, 'min': 5, 'max': 60},
            }
        },
    ],
    'mean_reversion': [
        {
            'id': 'rsi',
            'name': 'RSI Mean Reversion',
            'description': 'Buy oversold, sell overbought',
            'parameters': {
                'rsi_period': {'type': 'int', 'default': 14, 'min': 5, 'max': 30},
                'rsi_lower': {'type': 'float', 'default': 30, 'min': 10, 'max': 40},
                'rsi_upper': {'type': 'float', 'default': 70, 'min': 60, 'max': 90},
            }
        },
        {
            'id': 'bollinger',
            'name': 'Bollinger Bands',
            'description': 'Trade band breakouts',
            'parameters': {
                'bb_period': {'type': 'int', 'default': 20, 'min': 10, 'max': 50},
                'bb_devfactor': {'type': 'float', 'default': 2.0, 'min': 1.0, 'max': 3.0},
            }
        },
    ],
    'risk_managed': [
        {
            'id': 'dual_ma_stop',
            'name': 'Dual MA with Stop Loss',
            'description': 'MA crossover with risk management',
            'parameters': {
                'fast_period': {'type': 'int', 'default': 10, 'min': 2, 'max': 50},
                'slow_period': {'type': 'int', 'default': 30, 'min': 5, 'max': 200},
                'stop_loss_pct': {'type': 'float', 'default': 5.0, 'min': 1.0, 'max': 20.0},
                'take_profit_pct': {'type': 'float', 'default': 10.0, 'min': 2.0, 'max': 50.0},
            }
        },
    ],
}


def get_strategy_class(strategy_id: str):
    """Get strategy class by ID"""
    strategy_map = {
        'ma_cross': MovingAverageCrossStrategy,
        'ema_cross': EMACrossStrategy,
        'rsi': RSIStrategy,
        'bollinger': BollingerBandsStrategy,
        'macd': MACDStrategy,
        'dual_ma_stop': DualMAStrategyWithStop,
        'momentum': MomentumStrategy,
    }
    return strategy_map.get(strategy_id)


def get_strategy_catalog():
    """Return the complete strategy catalog"""
    return STRATEGY_CATALOG
