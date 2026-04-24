"""
Portfolio Management Module for China Assets

Supports:
- A-share portfolio construction and rebalancing
- Sector allocation for Chinese market
- Risk parity and equal weight strategies
- Position sizing with China-specific constraints
- Performance attribution by sector/industry
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class ChinaAssetPortfolio:
    """
    Portfolio manager for Chinese assets (A-shares, HK stocks, futures)

    Features:
    - Multiple weighting schemes (equal, inverse vol, risk parity)
    - Sector-based allocation
    - Position limits and constraints
    - Rebalancing strategies
    - Performance attribution
    """

    def __init__(self, initial_capital: float = 1000000.0):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions: Dict[str, Dict[str, Any]] = {}
        self.history: List[Dict[str, Any]] = []
        self.sector_map: Dict[str, str] = {}

    def set_sector_map(self, sector_map: Dict[str, str]):
        """Set sector classification for stocks"""
        self.sector_map = sector_map

    def add_asset(self, symbol: str, weight: float = 0.0,
                  max_position: float = 0.1, min_position: float = 0.0):
        """Add asset to portfolio"""
        self.positions[symbol] = {
            'symbol': symbol,
            'target_weight': weight,
            'current_weight': 0.0,
            'quantity': 0,
            'avg_cost': 0.0,
            'current_price': 0.0,
            'market_value': 0.0,
            'pnl': 0.0,
            'pnl_pct': 0.0,
            'max_position': max_position,
            'min_position': min_position,
            'sector': self.sector_map.get(symbol, 'Unknown'),
        }

    def calculate_weights_equal(self) -> Dict[str, float]:
        """Equal weight allocation"""
        n = len(self.positions)
        if n == 0:
            return {}
        weight = 1.0 / n
        return {sym: weight for sym in self.positions.keys()}

    def calculate_weights_inverse_vol(self, returns_data: pd.DataFrame,
                                       lookback: int = 60) -> Dict[str, float]:
        """Inverse volatility weighting"""
        weights = {}
        total_inv_vol = 0.0

        for sym in self.positions.keys():
            if sym in returns_data.columns:
                rets = returns_data[sym].tail(lookback)
                vol = rets.std()
                if vol > 0:
                    inv_vol = 1.0 / vol
                    weights[sym] = inv_vol
                    total_inv_vol += inv_vol
                else:
                    weights[sym] = 0.0
            else:
                weights[sym] = 0.0

        # Normalize
        if total_inv_vol > 0:
            weights = {k: v / total_inv_vol for k, v in weights.items()}
        else:
            weights = self.calculate_weights_equal()

        return weights

    def calculate_weights_risk_parity(self, returns_data: pd.DataFrame,
                                       lookback: int = 60) -> Dict[str, float]:
        """Risk parity allocation (simplified)"""
        n = len(self.positions)
        if n == 0:
            return {}

        # Calculate covariance matrix
        symbols = list(self.positions.keys())
        valid_symbols = [s for s in symbols if s in returns_data.columns]

        if len(valid_symbols) < 2:
            return self.calculate_weights_equal()

        cov_matrix = returns_data[valid_symbols].tail(lookback).cov()

        # Simplified risk parity: equal risk contribution
        # In practice, this requires iterative optimization
        weights = {}
        total_risk = 0.0

        for sym in valid_symbols:
            marginal_risk = cov_matrix.loc[sym, sym]
            if marginal_risk > 0:
                risk_contrib = 1.0 / np.sqrt(marginal_risk)
                weights[sym] = risk_contrib
                total_risk += risk_contrib

        # Normalize
        if total_risk > 0:
            weights = {k: v / total_risk for k, v in weights.items()}

        # Add missing symbols with zero weight
        for sym in symbols:
            if sym not in weights:
                weights[sym] = 0.0

        return weights

    def calculate_weights_momentum(self, returns_data: pd.DataFrame,
                                    lookback: int = 20,
                                    top_n: Optional[int] = None) -> Dict[str, float]:
        """Momentum-based weighting"""
        momentum_scores = {}

        for sym in self.positions.keys():
            if sym in returns_data.columns:
                rets = returns_data[sym].tail(lookback)
                total_ret = (1 + rets).prod() - 1
                momentum_scores[sym] = total_ret
            else:
                momentum_scores[sym] = 0.0

        # Select top N assets if specified
        if top_n and top_n < len(momentum_scores):
            sorted_assets = sorted(momentum_scores.items(), key=lambda x: x[1], reverse=True)
            selected = [a[0] for a in sorted_assets[:top_n]]
            # Zero out non-selected
            for sym in momentum_scores:
                if sym not in selected:
                    momentum_scores[sym] = 0.0

        # Weight by momentum score (only positive momentum)
        total_momentum = sum(max(0, v) for v in momentum_scores.values())

        if total_momentum > 0:
            weights = {k: max(0, v) / total_momentum for k, v in momentum_scores.items()}
        else:
            weights = self.calculate_weights_equal()

        return weights

    def rebalance(self, prices: pd.DataFrame, weights: Dict[str, float],
                  date: str) -> Dict[str, Any]:
        """Rebalance portfolio to target weights"""
        trades = []
        total_value = self.current_capital

        # Calculate current portfolio value
        for sym, pos in self.positions.items():
            if sym in prices.columns:
                price = prices[sym].iloc[-1]
                pos['current_price'] = price
                pos['market_value'] = pos['quantity'] * price
                pos['pnl'] = (price - pos['avg_cost']) * pos['quantity'] if pos['avg_cost'] > 0 else 0
                pos['pnl_pct'] = (price / pos['avg_cost'] - 1) * 100 if pos['avg_cost'] > 0 else 0

        # Calculate target values
        for sym, target_weight in weights.items():
            if sym not in self.positions:
                continue

            pos = self.positions[sym]
            target_value = total_value * target_weight

            # Apply position limits
            max_val = total_value * pos['max_position']
            min_val = total_value * pos['min_position']
            target_value = max(min_val, min(max_val, target_value))

            if sym in prices.columns:
                price = prices[sym].iloc[-1]
                target_quantity = int(target_value / price / 100) * 100  # Round to lot size (100 shares)

                current_quantity = pos['quantity']
                quantity_change = target_quantity - current_quantity

                if quantity_change != 0:
                    trade_type = 'buy' if quantity_change > 0 else 'sell'
                    trade_value = abs(quantity_change) * price
                    commission = trade_value * 0.0003  # 0.03% commission

                    trades.append({
                        'date': date,
                        'symbol': sym,
                        'action': trade_type,
                        'quantity': abs(quantity_change),
                        'price': price,
                        'value': trade_value,
                        'commission': commission,
                    })

                    # Update position
                    if trade_type == 'buy':
                        total_cost = pos['avg_cost'] * current_quantity + trade_value
                        pos['quantity'] = current_quantity + quantity_change
                        pos['avg_cost'] = total_cost / pos['quantity'] if pos['quantity'] > 0 else 0
                        self.current_capital -= (trade_value + commission)
                    else:
                        pos['quantity'] = current_quantity + quantity_change
                        self.current_capital += (trade_value - commission)

                    pos['current_weight'] = target_weight

        # Record history
        portfolio_value = self.get_portfolio_value(prices)
        self.history.append({
            'date': date,
            'portfolio_value': portfolio_value,
            'cash': self.current_capital,
            'num_trades': len(trades),
            'positions': {sym: pos.copy() for sym, pos in self.positions.items()},
        })

        return {
            'date': date,
            'trades': trades,
            'portfolio_value': portfolio_value,
            'num_trades': len(trades),
        }

    def get_portfolio_value(self, prices: pd.DataFrame) -> float:
        """Calculate total portfolio value"""
        total = self.current_capital

        for sym, pos in self.positions.items():
            if sym in prices.columns and pos['quantity'] > 0:
                price = prices[sym].iloc[-1]
                total += pos['quantity'] * price

        return total

    def get_portfolio_returns(self, prices: pd.DataFrame) -> pd.Series:
        """Calculate portfolio returns over time"""
        if len(self.history) == 0:
            return pd.Series()

        values = [h['portfolio_value'] for h in self.history]
        dates = [h['date'] for h in self.history]

        returns_series = pd.Series(values, index=dates)
        return returns_series.pct_change().fillna(0)

    def get_performance_metrics(self, prices: pd.DataFrame,
                                 benchmark_symbol: str = '000300.SS') -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        if len(self.history) < 2:
            return {}

        portfolio_values = pd.Series([h['portfolio_value'] for h in self.history])
        portfolio_returns = portfolio_values.pct_change().dropna()

        # Basic metrics
        total_return = (portfolio_values.iloc[-1] / portfolio_values.iloc[0]) - 1
        n_days = len(portfolio_returns)
        annual_return = (1 + total_return) ** (252 / max(n_days, 1)) - 1

        volatility = portfolio_returns.std() * np.sqrt(252)
        sharpe = annual_return / volatility if volatility > 0 else 0

        # Drawdown
        cumulative = (1 + portfolio_returns).cumprod()
        rolling_max = cumulative.cummax()
        drawdown = (cumulative - rolling_max) / rolling_max
        max_drawdown = drawdown.min()

        # Benchmark comparison
        benchmark_returns = self._get_benchmark_returns(prices, benchmark_symbol)
        if benchmark_returns is not None and len(benchmark_returns) > 0:
            # Align lengths
            min_len = min(len(portfolio_returns), len(benchmark_returns))
            port_rets = portfolio_returns.tail(min_len).values
            bench_rets = benchmark_returns.tail(min_len).values

            # Alpha and Beta
            if len(port_rets) > 1:
                beta = np.cov(port_rets, bench_rets)[0, 1] / np.var(bench_rets) if np.var(bench_rets) > 0 else 0
                alpha = annual_return - (0.03 + beta * (benchmark_returns.mean() * 252 - 0.03))
            else:
                alpha = 0
                beta = 0
        else:
            alpha = 0
            beta = 0

        return {
            'total_return': float(total_return),
            'annual_return': float(annual_return),
            'volatility': float(volatility),
            'sharpe_ratio': float(sharpe),
            'max_drawdown': float(max_drawdown),
            'alpha': float(alpha),
            'beta': float(beta),
            'num_periods': n_days,
            'final_value': float(portfolio_values.iloc[-1]),
            'initial_value': float(portfolio_values.iloc[0]),
        }

    def get_sector_allocation(self) -> Dict[str, float]:
        """Get current sector allocation"""
        sector_weights = {}

        for sym, pos in self.positions.items():
            sector = pos.get('sector', 'Unknown')
            if sector not in sector_weights:
                sector_weights[sector] = 0.0
            sector_weights[sector] += pos.get('current_weight', 0.0)

        return sector_weights

    def get_position_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all positions"""
        summary = []

        for sym, pos in self.positions.items():
            summary.append({
                'symbol': sym,
                'sector': pos.get('sector', 'Unknown'),
                'quantity': pos['quantity'],
                'avg_cost': pos['avg_cost'],
                'current_price': pos['current_price'],
                'market_value': pos['market_value'],
                'pnl': pos['pnl'],
                'pnl_pct': pos['pnl_pct'],
                'weight': pos['current_weight'],
            })

        return summary

    def _get_benchmark_returns(self, prices: pd.DataFrame,
                                benchmark_symbol: str) -> Optional[pd.Series]:
        """Get benchmark returns"""
        if benchmark_symbol in prices.columns:
            return prices[benchmark_symbol].pct_change().fillna(0)
        return None


def create_china_portfolio(initial_capital: float = 1000000.0,
                            symbols: Optional[List[str]] = None,
                            weighting_scheme: str = 'equal') -> ChinaAssetPortfolio:
    """
    Factory function to create a China asset portfolio

    Args:
        initial_capital: Initial capital amount
        symbols: List of stock symbols
        weighting_scheme: 'equal', 'inv_vol', 'risk_parity', 'momentum'

    Returns:
        ChinaAssetPortfolio instance
    """
    portfolio = ChinaAssetPortfolio(initial_capital)

    if symbols:
        for sym in symbols:
            portfolio.add_asset(sym)

    return portfolio
