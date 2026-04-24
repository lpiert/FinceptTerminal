"""
Backtrader Provider - Professional Event-Driven Backtesting

Full-featured backtesting using the Backtrader framework with support for:
- A-shares, HK stocks, China futures via AkShare data feeds
- Multiple built-in strategies (MA crossover, RSI, Bollinger Bands, MACD)
- Comprehensive performance analytics (Sharpe, Sortino, Drawdown, etc.)
- Parameter optimization and walk-forward analysis
- Multi-timeframe support

Uses Backtrader framework (GPL v3, v1.9.78+) with pandas integration.
"""

from .backtrader_provider import BacktraderProvider
from .br_portfolio import ChinaAssetPortfolio, create_china_portfolio
from .br_risk_monitor import RiskMonitor, RiskAlert, AlertLevel, AlertType, create_risk_monitor

__all__ = [
    'BacktraderProvider',
    'ChinaAssetPortfolio',
    'create_china_portfolio',
    'RiskMonitor',
    'RiskAlert',
    'AlertLevel',
    'AlertType',
    'create_risk_monitor',
]
