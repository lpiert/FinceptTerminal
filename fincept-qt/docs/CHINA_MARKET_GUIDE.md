# 中国市场接入指南

本文档说明如何在 Fincept Terminal 中使用中国金融市场数据。

---

## 📊 支持的市场

### 1. A股市场 (Shanghai & Shenzhen)

**Symbol 格式:**
- 上交所: `600519.SS` (贵州茅台)
- 深交所: `000001.SZ` (平安银行)
- 创业板: `300750.SZ` (宁德时代)
- 科创板: `688xxx.SS`
- 北交所: `8xxxxx.BJ`

**支持的数据:**
- ✅ 实时行情（价格、涨跌幅、成交量）
- ✅ 历史K线（日线、周线、月线）
- ✅ 财务指标（PE、PB、市值等）
- ⚠️ Level 2 深度数据（暂不支持）

### 2. 港股市场 (Hong Kong)

**Symbol 格式:**
- `0700.HK` (腾讯控股)
- `9988.HK` (阿里巴巴)
- `0005.HK` (汇丰控股)

**支持的数据:**
- ✅ 实时行情
- ✅ 历史K线
- ✅ 港股通标的

### 3. 中国期货 (Futures)

**交易所代码:**
- `SHF` - 上海期货交易所 (铜、黄金、原油等)
- `DCE` - 大连商品交易所 (铁矿石、豆粕等)
- `CZC` - 郑州商品交易所 (棉花、白糖等)
- `CFX` - 中国金融期货交易所 (股指期货、国债期货)

**Symbol 示例:**
- `rb2405.SHF` - 螺纹钢2405合约
- `au2406.SHF` - 黄金2406合约
- `IF2405.CFX` - 沪深300股指期货2405合约
- `i2405.DCE` - 铁矿石2405合约

### 4. ETF与期权

**ETF示例:**
- `510300.SS` - 沪深300ETF
- `510500.SS` - 中证500ETF
- `159919.SZ` - 沪深300ETF (深圳)

**期权格式:**
- `510300C3500.SSO` - 沪深300ETF认购期权 (行权价3.5)

---

## 🔧 使用方法

### 方法1: Python脚本直接调用

```bash
# 获取A股实时行情
python scripts/china_market_data.py --symbols 600519.SS,000001.SZ --type quote

# 获取历史K线
python scripts/china_market_data.py --symbol 600519.SS --period 1y --interval 1d --type history

# 获取期货行情
python scripts/china_market_data.py --symbols rb2405.SHF,IF2405.CFX --type quote
```

**输出格式:**
```json
{
  "success": true,
  "data": [
    {
      "symbol": "600519.SS",
      "name": "贵州茅台",
      "price": 1700.00,
      "change": 20.00,
      "change_pct": 1.19,
      "high": 1720.00,
      "low": 1680.00,
      "volume": 1234567,
      "timestamp": 1234567890,
      "exchange": "SSE"
    }
  ],
  "count": 1,
  "timestamp": 1234567890
}
```

### 方法2: C++ DataHub订阅

```cpp
#include "datahub/DataHub.h"
#include "services/markets/MarketDataService.h"

// 订阅A股行情
DataHub::instance().subscribe<QuoteData>(
    this,
    "market:quote:600519.SS",
    [this](const QuoteData& quote) {
        ui->priceLabel->setText(QString::number(quote.price));
        ui->changeLabel->setText(QString::number(quote.change_pct) + "%");
    }
);

// 订阅期货行情
DataHub::instance().subscribe<QuoteData>(
    this,
    "market:quote:rb2405.SHF",
    [this](const QuoteData& quote) {
        update_futures_display(quote);
    }
);

// 订阅历史数据
DataHub::instance().subscribe<QVector<HistoryPoint>>(
    this,
    "market:history:600519.SS:1y:1d",
    [this](const QVector<HistoryPoint>& history) {
        render_kline_chart(history);
    }
);
```

### 方法3: 添加默认观察列表

```cpp
// 在 Dashboard 或 Watchlist 中使用
auto a_shares = MarketDataService::china_a_share_symbols();
auto futures = MarketDataService::china_futures_symbols();
auto etfs = MarketDataService::china_etf_symbols();
auto hk_stocks = MarketDataService::china_hk_stock_symbols();

// 订阅批量行情
for (const auto& symbol : a_shares) {
    DataHub::instance().subscribe<QuoteData>(
        this,
        "market:quote:" + symbol,
        update_widget
    );
}
```

---

## 🎯 常用Symbol列表

### A股核心资产
```
600519.SS  贵州茅台 (白酒龙头)
601318.SS  中国平安 (保险龙头)
600036.SS  招商银行 (银行龙头)
000858.SZ  五粮液 (白酒)
002594.SZ  比亚迪 (新能源车)
300750.SZ  宁德时代 (动力电池)
000333.SZ  美的集团 (家电)
601012.SS  隆基绿能 (光伏)
```

### 股指期货
```
IF2405.CFX  沪深300股指期货
IC2405.CFX  中证500股指期货
IH2405.CFX  上证50股指期货
```

### 商品期货主力
```
rb2405.SHF   螺纹钢
au2406.SHF   黄金
cu2405.SHF   铜
i2405.DCE    铁矿石
TA2405.CZC   PTA
```

### 主要ETF
```
510300.SS  沪深300ETF
510500.SS  中证500ETF
510050.SS  上证50ETF
512880.SS  证券公司ETF
512660.SS  军工ETF
```

### 港股科技
```
0700.HK  腾讯控股
9988.HK  阿里巴巴
3690.HK  美团
1024.HK  快手
9618.HK  京东
```

---

## ⚙️ 配置要求

### Python依赖

确保已安装 `akshare`:

```bash
pip install akshare pandas
```

### 数据源说明

- **实时行情**: AkShare (东方财富接口)
- **历史数据**: AkShare (新浪财经接口)
- **更新频率**: 
  - 交易时段: ~3秒延迟
  - 非交易时段: 返回最后收盘价

---

## 🚀 性能优化

### 1. 批量请求

一次请求多个symbol，减少Python进程启动开销：

```cpp
// ✅ 推荐: 批量请求
QStringList symbols = {"600519.SS", "000001.SZ", "300750.SZ"};
MarketDataService::instance().fetch_quotes(symbols, callback);

// ❌ 避免: 逐个请求
for (const auto& sym : symbols) {
    MarketDataService::instance().fetch_quotes({sym}, callback);
}
```

### 2. 缓存策略

DataHub自动缓存行情数据：
- **TTL**: 30秒
- **最小刷新间隔**: 5秒
- 同一symbol在30秒内多次订阅，只触发一次Python调用

### 3. 按需订阅

只在需要时订阅topic，避免不必要的后台刷新：

```cpp
// 页面显示时订阅
void MyScreen::showEvent(QShowEvent*) {
    DataHub::instance().subscribe<QuoteData>(this, "market:quote:600519.SS", handler);
}

// 页面隐藏时自动取消订阅 (QObject销毁时自动清理)
```

---

## 🐛 常见问题

### Q1: 为什么某些symbol返回空数据？

**原因:**
- Symbol格式错误 (应该是 `600519.SS` 而非 `600519`)
- 非交易时段 (夜间或周末)
- 停牌股票

**解决:**
检查stderr输出中的警告信息：
```cpp
LOG_WARN("MarketData", "China market fetch failed: ...");
```

### Q2: 期货合约如何滚动？

期货合约有到期日，需要在到期前切换到下一个主力合约：

```cpp
// 当前主力: rb2405 (2024年5月到期)
// 4月中旬应切换到: rb2410

QString get_current_main_contract(const QString& base_symbol) {
    // 实现主力合约自动切换逻辑
    // 可根据成交量/持仓量判断
}
```

### Q3: 如何获取Level 2数据？

目前AkShare免费版只提供Level 1行情。如需Level 2：
- 方案1: 购买商业数据源 (聚宽、米筐、Wind)
- 方案2: 通过券商API (需机构账户)

---

## 📈 下一步扩展

### 阶段1: 已完成 ✅
- [x] A股/港股/期货/ETF行情接入
- [x] 历史K线数据
- [x] DataHub集成
- [x] 默认观察列表

### 阶段2: 模拟交易 (待开发)
- [ ] A股交易规则引擎 (T+1, 涨跌停板)
- [ ] PaperTrading扩展
- [ ] 回测框架适配

### 阶段3: 实盘接口 (需合规资质)
- [ ] CTP接口封装 (期货)
- [ ] XTP接口封装 (股票)
- [ ] Broker适配器实现
- [ ] 风控模块

---

## 📞 技术支持

遇到问题请查看:
1. Python脚本日志: `logs/fincept.log`
2. DataHub状态: 内置 DevTools → DataHub Inspector
3. AkShare文档: https://akshare.akfamily.xyz/

---

**最后更新**: 2026-04-20
**版本**: v1.0 (中国市场基础行情)
