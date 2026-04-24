# 快速开始 - Backtrader 集成

## 5分钟快速上手

### 1. 运行测试（验证安装）
```bash
cd fincept-qt/scripts/Analytics/backtesting
python bt_engine/test_backtrader.py
```

### 2. 运行回测
```python
from bt_engine import BacktraderProvider

provider = BacktraderProvider()

result = provider.run_backtest({
    'strategy': {
        'type': 'ma_cross',
        'parameters': {'fast_period': 5, 'slow_period': 20}
    },
    'startDate': '2023-01-01',
    'endDate': '2023-06-01',
    'initialCapital': 100000,
    'assets': [{'symbol': '600519.SS'}]
})

print(f"Total Return: {result['data']['performance']['totalReturn']:.2%}")
```

### 3. 创建 Portfolio
```python
from bt_engine import create_china_portfolio

portfolio = create_china_portfolio(
    initial_capital=1000000,
    symbols=['600519.SS', '000001.SZ', '600036.SS']
)

weights = portfolio.calculate_weights_equal()
print(weights)
```

### 4. 监控风险
```python
from bt_engine import create_risk_monitor

monitor = create_risk_monitor()
summary = monitor.get_risk_summary()
print(f"Risk Level: {summary['risk_level']}")
```

## 常用命令

```bash
# 交互式调试
python bt_engine/debug_backtest.py

# Portfolio 测试
python bt_engine/test_portfolio.py

# 风险监控测试
python bt_engine/test_risk_monitor.py

# 命令行回测
python bt_engine/backtrader_provider.py run_backtest '{"strategy":{"type":"ma_cross"},"assets":[{"symbol":"600519.SS"}],"startDate":"2023-01-01","endDate":"2023-06-01","initialCapital":100000}'
```

## 可用策略

- `ma_cross` - MA 交叉
- `ema_cross` - EMA 交叉
- `rsi` - RSI 策略
- `macd` - MACD 策略
- `bollinger` - 布林带
- `momentum` - 动量策略
- `dual_ma_stop` - 双均线+止损

## 文档

- `README.md` - 完整使用指南
- `IMPLEMENTATION_SUMMARY.md` - 实现总结
- 代码注释 - 每个函数都有说明
