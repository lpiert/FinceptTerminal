# Backtrader Provider - 使用指南

## 快速开始

### 1. 运行调试工具（推荐）

```bash
# Windows
cd fincept-qt\scripts\Analytics\backtesting
python bt_engine\debug_backtest.py

# 或者直接双击
run_bt.bat
```

### 2. VSCode 调试

按 `F5` 或点击调试面板，选择以下配置之一：

- **Backtrader: Debug Test** - 交互式调试工具（推荐）
- **Backtrader: Run Single Backtest** - 运行单个回测
- **Backtrader: Test Provider** - 运行测试套件
- **Backtrader: CLI Command** - 命令行模式

### 3. 命令行直接调用

```bash
# 测试连接
python bt_engine/backtrader_provider.py test_connection "{}"

# 获取策略列表
python bt_engine/backtrader_provider.py get_strategies "{}"

# 运行回测
python bt_engine/backtrader_provider.py run_backtest "{\"strategy\":{\"type\":\"ma_cross\",\"parameters\":{\"fast_period\":5,\"slow_period\":20}},\"startDate\":\"2023-01-01\",\"endDate\":\"2023-06-01\",\"initialCapital\":100000,\"commission\":0.0003,\"assets\":[{\"symbol\":\"600519.SS\"}]}"
```

## Python API 使用

### 基础用法

```python
from bt_engine.backtrader_provider import BacktraderProvider

# 创建 provider
provider = BacktraderProvider()

# 测试连接
result = provider.test_connection()
print(result)

# 运行回测
result = provider.run_backtest({
    'strategy': {
        'type': 'ma_cross',
        'parameters': {
            'fast_period': 5,
            'slow_period': 20
        }
    },
    'startDate': '2023-01-01',
    'endDate': '2023-06-01',
    'initialCapital': 100000,
    'commission': 0.0003,
    'assets': [{'symbol': '600519.SS'}]
})

if result['success']:
    perf = result['data']['performance']
    print(f"Total Return: {perf['totalReturn']:.2%}")
    print(f"Sharpe Ratio: {perf['sharpeRatio']:.3f}")
    print(f"Max Drawdown: {perf['maxDrawdown']:.2%}")
```

### 参数优化

```python
result = provider.optimize({
    'strategy': {'type': 'ma_cross'},
    'startDate': '2023-01-01',
    'endDate': '2023-04-01',
    'initialCapital': 100000,
    'objective': 'sharpe',  # 优化目标：sharpe, return, calmar
    'method': 'grid',       # 方法：grid 或 random
    'maxIterations': 20,
    'parameters': {
        'fast_period': {'min': 3, 'max': 10, 'step': 1},
        'slow_period': {'min': 15, 'max': 30, 'step': 5},
    },
    'assets': [{'symbol': '600519.SS'}]
})

print(f"Best parameters: {result['data']['bestParameters']}")
print(f"Best score: {result['data']['bestScore']:.3f}")
```

### Walk-Forward 分析

```python
result = provider.walk_forward({
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
})

for split in result['data']['splits']:
    print(f"Split {split['split']}: Return={split['totalReturn']:.2%}")
```

### 技术指标计算

```python
result = provider.calculate_indicator({
    'indicator': 'rsi',
    'parameters': {'period': 14},
    'symbols': ['600519.SS'],
    'startDate': '2023-01-01',
    'endDate': '2023-06-01'
})

print(result['data']['results'])
```

## 可用策略

### 趋势跟踪
- `ma_cross` - 移动平均线交叉
- `ema_cross` - 指数移动平均线交叉
- `macd` - MACD 信号
- `momentum` - 动量策略

### 均值回归
- `rsi` - RSI 超买超卖
- `bollinger` - 布林带突破

### 风险管理
- `dual_ma_stop` - 双均线 + 止损止盈

## 支持的资产

- **A股**: `600519.SS` (贵州茅台), `000001.SZ` (平安银行)
- **港股**: 通过 AkShare 支持
- **期货**: 中国期货市场数据

## 调试技巧

### 1. 设置断点

在 VSCode 中打开 `backtrader_provider.py`，在任意行点击左侧设置断点，然后使用调试配置运行。

### 2. 查看变量

在调试过程中，可以在调试面板查看：
- `request` - 输入参数
- `result` - 返回结果
- `cerebro` - Backtrader 引擎状态

### 3. 修改测试参数

编辑 `debug_backtest.py` 中的 `config` 字典来测试不同场景：

```python
config = {
    'strategy': {
        'type': 'rsi',  # 改为其他策略
        'parameters': {
            'rsi_period': 14,
            'rsi_lower': 30,
            'rsi_upper': 70,
        }
    },
    # ... 其他参数
}
```

### 4. 查看详细日志

运行时添加环境变量：

```bash
set PYTHONVERBOSE=1
python bt_engine/debug_backtest.py
```

## 常见问题

### Q: 导入错误 "No module named 'backtrader'"
A: 安装依赖：`pip install backtrader akshare`

### Q: 数据获取失败
A: 检查网络连接，AkShare 需要访问互联网获取实时数据

### Q: 回测结果为负
A: 可能是策略参数不佳，尝试使用优化功能找到更好的参数

### Q: 如何添加自定义策略？
A: 在 `br_strategies.py` 中添加新的策略类，继承 `bt.Strategy`，然后在 `STRATEGY_CATALOG` 中注册。

## 性能指标说明

- **Total Return**: 总收益率
- **Annualized Return**: 年化收益率
- **Sharpe Ratio**: 夏普比率（风险调整后收益）
- **Sortino Ratio**: 索提诺比率（下行风险调整）
- **Max Drawdown**: 最大回撤
- **Win Rate**: 胜率
- **Calmar Ratio**: 卡玛比率（收益/最大回撤）

## 下一步

- 添加更多策略
- 实现多资产组合回测
- 添加实时交易接口
- 集成机器学习模型
