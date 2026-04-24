# 中国市场数据 - 快速开始

## 📦 安装依赖

### 1. 安装 AkShare

```bash
pip install akshare pandas
```

**国内镜像加速:**
```bash
pip install akshare pandas -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 验证安装

```bash
python scripts/china_market_data.py --symbols 600519.SS --type quote
```

预期输出:
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
      ...
    }
  ],
  "count": 1
}
```

---

## 🚀 在 Fincept Terminal 中使用

### 方法1: Dashboard添加A股Widget

1. 打开 Dashboard
2. 点击 "Add Widget" → "Market Pulse"
3. 在Symbol列表中选择中国股票:
   - `600519.SS` (贵州茅台)
   - `000001.SZ` (平安银行)
   - `300750.SZ` (宁德时代)

### 方法2: Watchlist创建A股观察列表

1. 打开 Watchlist Screen
2. 新建列表 "A股核心资产"
3. 添加以下Symbols:
   ```
   600519.SS
   601318.SS
   600036.SS
   000858.SZ
   002594.SZ
   300750.SZ
   ```

### 方法3: K线图查看历史数据

1. 打开 Markets Screen
2. 输入Symbol: `600519.SS`
3. 选择周期: 1D / 1W / 1M
4. 图表自动加载历史K线

---

## 📊 支持的品种速查

### A股热门股票
```
600519.SS  贵州茅台
601318.SS  中国平安
600036.SS  招商银行
000858.SZ  五粮液
002594.SZ  比亚迪
300750.SZ  宁德时代
```

### 股指期货
```
IF2405.CFX  沪深300股指期货
IC2405.CFX  中证500股指期货
IH2405.CFX  上证50股指期货
```

### 商品期货主力
```
rb2405.SHF  螺纹钢
au2406.SHF  黄金
cu2405.SHF  铜
i2405.DCE   铁矿石
```

### ETF基金
```
510300.SS  沪深300ETF
510500.SS  中证500ETF
512880.SS  券商ETF
```

### 港股科技股
```
0700.HK  腾讯控股
9988.HK  阿里巴巴
3690.HK  美团
```

---

## ⚙️ C++开发集成

### 订阅A股行情

```cpp
#include "datahub/DataHub.h"
#include "services/markets/MarketDataService.h"

// 在Widget或Screen中订阅
void MyWidget::setup_data_subscription() {
    DataHub::instance().subscribe<QuoteData>(
        this,
        "market:quote:600519.SS",
        [this](const QuoteData& quote) {
            ui->priceLabel->setText(QString::number(quote.price));
            ui->changeLabel->setText(
                QString("%1%").arg(quote.change_pct, 0, 'f', 2)
            );
        }
    );
}
```

### 批量获取A股列表

```cpp
// 获取预定义的A股列表
auto a_shares = MarketDataService::china_a_share_symbols();
auto futures = MarketDataService::china_futures_symbols();
auto etfs = MarketDataService::china_etf_symbols();
auto hk_stocks = MarketDataService::china_hk_stock_symbols();

// 批量订阅
for (const auto& symbol : a_shares) {
    DataHub::instance().subscribe<QuoteData>(
        this,
        "market:quote:" + symbol,
        update_handler
    );
}
```

### 获取历史K线

```cpp
// 订阅历史数据
DataHub::instance().subscribe<QVector<HistoryPoint>>(
    this,
    "market:history:600519.SS:1y:1d",  // 1年日线
    [this](const QVector<HistoryPoint>& history) {
        // 渲染K线图
        render_candlestick_chart(history);
    }
);

// 手动请求刷新
DataHub::instance().request("market:history:600519.SS:1y:1d");
```

---

## 🔧 故障排查

### 问题1: "Missing dependency: akshare"

**解决:**
```bash
pip install akshare
```

### 问题2: 返回空数据

**可能原因:**
- Symbol格式错误（应为 `600519.SS` 而非 `600519`）
- 非交易时段（返回最后收盘价）
- 股票停牌

**检查方法:**
```bash
python scripts/china_market_data.py --symbols 600519.SS --type quote
# 查看stderr输出的警告信息
```

### 问题3: 数据更新慢

**原因:**
- DataHub默认30秒TTL缓存
- 最小刷新间隔5秒

**调整策略（修改C++代码）:**
```cpp
// 在 MarketDataService::ensure_registered_with_hub() 中
datahub::TopicPolicy policy;
policy.ttl_ms = 10'000;  // 改为10秒TTL
policy.min_interval_ms = 2'000;  // 改为2秒最小间隔
hub.set_policy_pattern("market:quote:*", policy);
```

---

## 📈 下一步

1. **阶段1 (已完成)**: 行情数据接入 ✅
2. **阶段2**: 模拟交易支持 (待开发)
3. **阶段3**: 实盘接口 (需合规资质)

详细文档请查看:
- [CHINA_MARKET_GUIDE.md](CHINA_MARKET_GUIDE.md) - 完整使用指南
- [DATAHUB_ARCHITECTURE.md](../DATAHUB_ARCHITECTURE.md) - DataHub架构说明

---

**技术支持**: 遇到问题请查看 `logs/fincept.log` 日志文件
