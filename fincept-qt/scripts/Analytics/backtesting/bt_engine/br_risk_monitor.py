"""
Risk Monitoring and Alert System for China Assets

Features:
- Real-time risk metrics monitoring
- Position concentration alerts
- Drawdown warnings
- Volatility spikes detection
- Correlation breakdown alerts
- Sector exposure limits
- Stop-loss monitoring
- VaR (Value at Risk) calculations
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


class AlertType(Enum):
    """Types of risk alerts"""
    DRAWDOWN = "drawdown"
    VOLATILITY = "volatility"
    CONCENTRATION = "concentration"
    CORRELATION = "correlation"
    VAR_BREACH = "var_breach"
    STOP_LOSS = "stop_loss"
    SECTOR_LIMIT = "sector_limit"
    VOLUME_SPIKE = "volume_spike"
    PRICE_GAP = "price_gap"


class RiskAlert:
    """Single risk alert"""

    def __init__(self, alert_type: AlertType, level: AlertLevel,
                 message: str, symbol: str = '',
                 current_value: float = 0.0,
                 threshold: float = 0.0,
                 timestamp: Optional[str] = None):
        self.alert_type = alert_type
        self.level = level
        self.message = message
        self.symbol = symbol
        self.current_value = current_value
        self.threshold = threshold
        self.timestamp = timestamp or datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.alert_type.value,
            'level': self.level.value,
            'message': self.message,
            'symbol': self.symbol,
            'current_value': self.current_value,
            'threshold': self.threshold,
            'timestamp': self.timestamp,
        }


class RiskMonitor:
    """
    Comprehensive risk monitoring system for China asset portfolios

    Monitors:
    - Portfolio-level risks (drawdown, volatility, VaR)
    - Position-level risks (concentration, stop-loss)
    - Market-level risks (correlation, sector exposure)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # Default risk limits
        self.config = config or {}

        # Risk limits
        self.max_drawdown = self.config.get('max_drawdown', 0.10)  # 10%
        self.max_position_weight = self.config.get('max_position_weight', 0.20)  # 20%
        self.max_sector_weight = self.config.get('max_sector_weight', 0.40)  # 40%
        self.max_portfolio_vol = self.config.get('max_portfolio_vol', 0.30)  # 30%
        self.var_confidence = self.config.get('var_confidence', 0.95)  # 95%
        self.max_correlation = self.config.get('max_correlation', 0.8)  # 0.8

        # Stop loss levels
        self.stop_loss_levels = self.config.get('stop_loss_levels', {
            'warning': -0.05,   # -5%
            'critical': -0.10,  # -10%
            'emergency': -0.15, # -15%
        })

        # Alert history
        self.alerts: List[RiskAlert] = []
        self.alert_history: List[Dict[str, Any]] = []

    def check_portfolio_risks(self, portfolio_data: Dict[str, Any],
                               prices: pd.DataFrame,
                               returns: pd.DataFrame) -> List[RiskAlert]:
        """
        Check all portfolio-level risks

        Args:
            portfolio_data: Portfolio information (values, positions, etc.)
            prices: Price data DataFrame
            returns: Returns data DataFrame

        Returns:
            List of RiskAlert objects
        """
        alerts = []

        # Check drawdown
        alerts.extend(self._check_drawdown(portfolio_data))

        # Check volatility
        alerts.extend(self._check_volatility(returns))

        # Check position concentration
        alerts.extend(self._check_concentration(portfolio_data))

        # Check sector exposure
        alerts.extend(self._check_sector_exposure(portfolio_data))

        # Check VaR
        alerts.extend(self._check_var(returns, portfolio_data))

        # Check correlations
        alerts.extend(self._check_correlations(returns))

        # Store alerts
        self.alerts = alerts
        self.alert_history.extend([a.to_dict() for a in alerts])

        return alerts

    def check_position_risks(self, positions: List[Dict[str, Any]],
                              prices: pd.DataFrame) -> List[RiskAlert]:
        """Check individual position risks"""
        alerts = []

        for pos in positions:
            symbol = pos.get('symbol', '')
            if symbol not in prices.columns:
                continue

            # Check stop loss
            alerts.extend(self._check_stop_loss(pos, prices[symbol]))

            # Check volume spikes
            if 'volume' in prices.columns:
                alerts.extend(self._check_volume_spike(symbol, prices))

            # Check price gaps
            alerts.extend(self._check_price_gaps(symbol, prices))

        return alerts

    def _check_drawdown(self, portfolio_data: Dict[str, Any]) -> List[RiskAlert]:
        """Check portfolio drawdown"""
        alerts = []

        if 'portfolio_values' not in portfolio_data:
            return alerts

        values = portfolio_data['portfolio_values']
        if len(values) < 2:
            return alerts

        # Calculate drawdown
        rolling_max = values.cummax()
        drawdown = (values - rolling_max) / rolling_max
        current_dd = drawdown.iloc[-1]

        # Check against thresholds
        if abs(current_dd) > self.max_drawdown:
            level = AlertLevel.CRITICAL if abs(current_dd) > self.max_drawdown * 1.5 else AlertLevel.WARNING
            alerts.append(RiskAlert(
                alert_type=AlertType.DRAWDOWN,
                level=level,
                message=f"Portfolio drawdown {abs(current_dd):.1%} exceeds limit {self.max_drawdown:.1%}",
                current_value=current_dd,
                threshold=self.max_drawdown,
            ))

        return alerts

    def _check_volatility(self, returns: pd.DataFrame) -> List[RiskAlert]:
        """Check portfolio volatility"""
        alerts = []

        if returns.empty:
            return alerts

        # Calculate rolling volatility (20-day)
        window = min(20, len(returns))
        if window < 5:
            return alerts

        rolling_vol = returns.rolling(window=window).std() * np.sqrt(252)

        for col in returns.columns:
            if col in rolling_vol.columns:
                current_vol = rolling_vol[col].iloc[-1]
                avg_vol = rolling_vol[col].mean()

                # Check if volatility spiked
                if current_vol > self.max_portfolio_vol:
                    alerts.append(RiskAlert(
                        alert_type=AlertType.VOLATILITY,
                        level=AlertLevel.WARNING,
                        message=f"{col} volatility {current_vol:.1%} exceeds limit {self.max_portfolio_vol:.1%}",
                        symbol=col,
                        current_value=current_vol,
                        threshold=self.max_portfolio_vol,
                    ))
                elif current_vol > avg_vol * 2:
                    alerts.append(RiskAlert(
                        alert_type=AlertType.VOLATILITY,
                        level=AlertLevel.INFO,
                        message=f"{col} volatility spike: {current_vol:.1%} vs avg {avg_vol:.1%}",
                        symbol=col,
                        current_value=current_vol,
                        threshold=avg_vol * 2,
                    ))

        return alerts

    def _check_concentration(self, portfolio_data: Dict[str, Any]) -> List[RiskAlert]:
        """Check position concentration"""
        alerts = []

        positions = portfolio_data.get('positions', {})

        for symbol, pos in positions.items():
            weight = pos.get('current_weight', 0)

            if weight > self.max_position_weight:
                alerts.append(RiskAlert(
                    alert_type=AlertType.CONCENTRATION,
                    level=AlertLevel.WARNING,
                    message=f"{symbol} weight {weight:.1%} exceeds limit {self.max_position_weight:.1%}",
                    symbol=symbol,
                    current_value=weight,
                    threshold=self.max_position_weight,
                ))

        return alerts

    def _check_sector_exposure(self, portfolio_data: Dict[str, Any]) -> List[RiskAlert]:
        """Check sector exposure limits"""
        alerts = []

        sector_weights = portfolio_data.get('sector_weights', {})

        for sector, weight in sector_weights.items():
            if weight > self.max_sector_weight:
                alerts.append(RiskAlert(
                    alert_type=AlertType.SECTOR_LIMIT,
                    level=AlertLevel.WARNING,
                    message=f"Sector '{sector}' exposure {weight:.1%} exceeds limit {self.max_sector_weight:.1%}",
                    current_value=weight,
                    threshold=self.max_sector_weight,
                ))

        return alerts

    def _check_var(self, returns: pd.DataFrame,
                   portfolio_data: Dict[str, Any]) -> List[RiskAlert]:
        """Calculate and check Value at Risk"""
        alerts = []

        if returns.empty:
            return alerts

        portfolio_value = portfolio_data.get('portfolio_value', 0)

        # Calculate parametric VaR
        for col in returns.columns:
            rets = returns[col].dropna()
            if len(rets) < 20:
                continue

            mean_ret = rets.mean()
            std_ret = rets.std()

            # 95% VaR (assuming normal distribution)
            z_score = 1.645  # For 95% confidence
            var_95 = mean_ret - z_score * std_ret
            var_amount = abs(var_95 * portfolio_value)

            # Check if daily loss exceeds VaR
            latest_return = rets.iloc[-1]
            if latest_return < var_95:
                alerts.append(RiskAlert(
                    alert_type=AlertType.VAR_BREACH,
                    level=AlertLevel.WARNING,
                    message=f"{col} breached 95% VaR: {latest_return:.2%} < {var_95:.2%}",
                    symbol=col,
                    current_value=latest_return,
                    threshold=var_95,
                ))

        return alerts

    def _check_correlations(self, returns: pd.DataFrame) -> List[RiskAlert]:
        """Check correlation breakdown"""
        alerts = []

        if returns.shape[1] < 2:
            return alerts

        # Calculate correlation matrix
        corr_matrix = returns.tail(60).corr()  # Last 60 days

        # Check pairwise correlations
        checked = set()
        for i, sym1 in enumerate(corr_matrix.columns):
            for j, sym2 in enumerate(corr_matrix.columns):
                if i >= j:
                    continue

                pair = tuple(sorted([sym1, sym2]))
                if pair in checked:
                    continue
                checked.add(pair)

                corr = corr_matrix.loc[sym1, sym2]
                if abs(corr) > self.max_correlation:
                    alerts.append(RiskAlert(
                        alert_type=AlertType.CORRELATION,
                        level=AlertLevel.INFO,
                        message=f"High correlation between {sym1} and {sym2}: {corr:.2f}",
                        symbol=f"{sym1},{sym2}",
                        current_value=corr,
                        threshold=self.max_correlation,
                    ))

        return alerts

    def _check_stop_loss(self, position: Dict[str, Any],
                         prices: pd.Series) -> List[RiskAlert]:
        """Check stop loss levels for a position"""
        alerts = []

        avg_cost = position.get('avg_cost', 0)
        if avg_cost <= 0:
            return alerts

        current_price = prices.iloc[-1]
        pnl_pct = (current_price - avg_cost) / avg_cost

        symbol = position.get('symbol', '')

        for level_name, threshold in self.stop_loss_levels.items():
            if pnl_pct <= threshold:
                level_map = {
                    'warning': AlertLevel.WARNING,
                    'critical': AlertLevel.CRITICAL,
                    'emergency': AlertLevel.EMERGENCY,
                }
                alerts.append(RiskAlert(
                    alert_type=AlertType.STOP_LOSS,
                    level=level_map.get(level_name, AlertLevel.WARNING),
                    message=f"{symbol} hit {level_name} stop loss: {pnl_pct:.1%} <= {threshold:.1%}",
                    symbol=symbol,
                    current_value=pnl_pct,
                    threshold=threshold,
                ))
                break  # Only report the most severe level

        return alerts

    def _check_volume_spike(self, symbol: str,
                            prices: pd.DataFrame) -> List[RiskAlert]:
        """Check for unusual volume spikes"""
        alerts = []

        if 'volume' not in prices.columns:
            return alerts

        volumes = prices['volume'].tail(20)
        if len(volumes) < 10:
            return alerts

        avg_volume = volumes[:-1].mean()
        current_volume = volumes.iloc[-1]

        if avg_volume > 0 and current_volume > avg_volume * 3:
            alerts.append(RiskAlert(
                alert_type=AlertType.VOLUME_SPIKE,
                level=AlertLevel.INFO,
                message=f"{symbol} volume spike: {current_volume:.0f} vs avg {avg_volume:.0f}",
                symbol=symbol,
                current_value=current_volume,
                threshold=avg_volume * 3,
            ))

        return alerts

    def _check_price_gaps(self, symbol: str,
                          prices: pd.DataFrame) -> List[RiskAlert]:
        """Check for significant price gaps"""
        alerts = []

        if symbol not in prices.columns:
            return alerts

        close_prices = prices[symbol].tail(5)
        if len(close_prices) < 2:
            return alerts

        # Check overnight gap
        prev_close = close_prices.iloc[-2]
        curr_open = close_prices.iloc[-1]  # Using close as proxy

        gap_pct = abs(curr_open - prev_close) / prev_close

        if gap_pct > 0.05:  # 5% gap
            alerts.append(RiskAlert(
                alert_type=AlertType.PRICE_GAP,
                level=AlertLevel.WARNING,
                message=f"{symbol} price gap: {gap_pct:.1%}",
                symbol=symbol,
                current_value=float(gap_pct),
                threshold=0.05,
            ))

        return alerts

    def get_risk_summary(self) -> Dict[str, Any]:
        """Get summary of current risk status"""
        if not self.alerts:
            return {
                'status': 'NORMAL',
                'alert_count': 0,
                'risk_level': 'LOW',
            }

        # Count by level
        level_counts = {}
        for alert in self.alerts:
            level = alert.level.value
            level_counts[level] = level_counts.get(level, 0) + 1

        # Determine overall risk level
        if level_counts.get('EMERGENCY', 0) > 0:
            risk_level = 'EMERGENCY'
        elif level_counts.get('CRITICAL', 0) > 0:
            risk_level = 'HIGH'
        elif level_counts.get('WARNING', 0) > 0:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'

        return {
            'status': 'ALERT' if risk_level != 'LOW' else 'NORMAL',
            'risk_level': risk_level,
            'alert_count': len(self.alerts),
            'by_level': level_counts,
            'alerts': [a.to_dict() for a in self.alerts],
        }

    def get_alert_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent alert history"""
        return self.alert_history[-limit:]

    def clear_alerts(self):
        """Clear current alerts"""
        self.alerts = []


def create_risk_monitor(config: Optional[Dict[str, Any]] = None) -> RiskMonitor:
    """Factory function to create risk monitor with custom config"""
    return RiskMonitor(config)
