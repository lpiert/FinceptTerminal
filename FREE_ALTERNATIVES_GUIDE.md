# Fincept Terminal 完全免费使用指南

## 📋 概述

Fincept Terminal的**商业付费部分可以100%替换为免费开源方案**。本指南详细说明如何用免费数据源和服务替代所有付费功能。

---

## ✅ 已内置的免费数据源 (无需任何改动)

### 1. 市场数据 (Market Data)
| 数据源 | 覆盖范围 | API密钥 | 状态 |
|--------|---------|---------|------|
| **Yahoo Finance** | 全球股票、ETF、指数 | ❌ 不需要 | ✅ 已集成 |
| **AKShare** | 中国A股/港股/期货/债券/基金 | ❌ 不需要 | ✅ 已集成 |
| **BaoStock** | A股历史数据 | ❌ 不需要 | ✅ 已集成 |
| **CoinGecko** | 5000+加密货币 | ❌ 不需要 | ✅ 已集成 |
| **CoinCap** | 加密货币实时数据 | ❌ 不需要 | ✅ 已集成 |
| **Frankfurter** | 32种货币汇率(ECB) | ❌ 不需要 | ✅ 已集成 |

**脚本位置:**
```
fincept-qt/scripts/yfinance_data.py          # Yahoo Finance
fincept-qt/scripts/akshare_*.py              # AKShare (40+脚本)
fincept-qt/scripts/baostock_data.py          # BaoStock
fincept-qt/scripts/coingecko.py              # CoinGecko
```

### 2. 宏观经济数据 (Economic Data)
| 数据源 | 数据类型 | API密钥 | 状态 |
|--------|---------|---------|------|
| **FRED** | 美国经济指标(80万+序列) | 可选(提高限额) | ✅ 已集成 |
| **World Bank** | 全球发展指标(217国家) | ❌ 不需要 | ✅ 已集成 |
| **IMF** | 国际金融统计 | ❌ 不需要 | ✅ 已集成 |
| **OECD** | 经合组织统计数据 | ❌ 不需要 | ✅ 已集成 |
| **ECB** | 欧洲央行统计 | ❌ 不需要 | ✅ 已集成 |
| **BOE** | 英国央行数据 | ❌ 不需要 | ✅ 已集成 |
| **RBA** | 澳洲储备银行 | ❌ 不需要 | ✅ 已集成 |
| **BCB** | 巴西央行 | ❌ 不需要 | ✅ 已集成 |
| **各国统计局** | 100+国家官方数据 | ❌ 不需要 | ✅ 已集成 |

**脚本位置:**
```
fincept-qt/scripts/fred_data.py              # FRED
fincept-qt/scripts/worldbank_data.py         # World Bank
fincept-qt/scripts/imf_data.py               # IMF
fincept-qt/scripts/oecd_data.py              # OECD
fincept-qt/scripts/ecb_data.py               # ECB
fincept-qt/scripts/boe_data.py               # BOE
fincept-qt/scripts/rba_data.py               # RBA
```

### 3. 量化分析工具 (Quantitative Analysis)
| 工具库 | 功能 | 许可证 | 状态 |
|--------|------|--------|------|
| **QuantLib** | 衍生品定价(18模块) | BSD | ✅ 已集成 |
| **Backtrader** | 策略回测框架 | GPL v3 | ✅ 已集成 |
| **PyPortfolioOpt** | 投资组合优化 | LGPL | ✅ 已集成 |
| **TA-Lib/talipp** | 技术指标计算 | BSD | ✅ 已集成 |
| **Statsmodels** | 统计分析 | BSD | ✅ 已集成 |
| **Scikit-learn** | 机器学习 | BSD | ✅ 已集成 |
| **NumPy/Pandas** | 数值计算 | BSD | ✅ 已集成 |

**脚本位置:**
```
fincept-qt/scripts/backtest_engine.py        # Backtrader引擎
fincept-qt/scripts/optimize_portfolio_weights.py  # 组合优化
fincept-qt/scripts/quantstats_analysis.py    # 绩效分析
fincept-qt/scripts/Analytics/                # 30+量化分析模块
```

---

## 🔧 需要简单配置的免费替代方案

### 4. AI智能体与LLM (AI Agents)

#### 付费方案 vs 免费替代

| 付费方案 | 月费 | 免费替代 | 限制 |
|---------|------|---------|------|
| OpenAI GPT-4 | $20-200 | **Ollama** (本地) | 需要GPU |
| Anthropic Claude | $20-100 | **DeepSeek API** | 免费额度有限 |
| Gemini Pro | $0-50 | **Groq** | 免费层可用 |
| - | - | **HuggingFace** | 完全免费 |

#### 配置免费LLM

**方案A: Ollama (推荐,完全离线)**
```bash
# 安装Ollama
# Windows: 下载安装包 https://ollama.com/download
# macOS: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh

# 下载模型
ollama pull llama3.2        # 3B参数,轻量级
ollama pull mistral         # 7B参数,平衡性能
ollama pull qwen2.5         # 中文优化

# 在Fincept Terminal中配置
设置 → AI配置 → 选择 "Ollama" → 输入模型名称
```

**方案B: DeepSeek (免费API)**
```python
# 注册获取API Key: https://platform.deepseek.com
# 免费额度: 14元(约$2),足够个人使用数月

# 在Fincept Terminal中配置
设置 → AI配置 → 选择 "DeepSeek" → 输入API Key
```

**方案C: Groq (超快推理)**
```python
# 注册: https://console.groq.com
# 免费层: Llama 3.1 8B/70B, Mixtral 8x7B
# 速率限制: 30请求/分钟

# 在Fincept Terminal中配置
设置 → AI配置 → 选择 "Groq" → 输入API Key
```

**代码已支持多提供商切换:**
```cpp
// src/screens/settings/LlmConfigSection.cpp
// 支持的提供商: OpenAI, Anthropic, Gemini, Groq, DeepSeek, 
//              MiniMax, OpenRouter, Ollama
```

### 5. 新闻与情感分析 (News & Sentiment)

#### 免费数据源

| 数据源 | 类型 | API密钥 | 限制 |
|--------|------|---------|------|
| **Reddit API** | 零售情绪 | 需要(免费) | 100次/分钟 |
| **Twitter/X Free** | 社交媒体 | 需要(免费) | 1500推文/月 |
| **NewsAPI.org** | 新闻聚合 | 需要(免费) | 100次/天 |
| **GDELT Project** | 全球事件 | ❌ 不需要 | 完全免费 |
| **Polymarket** | 预测市场 | ❌ 不需要 | 已集成 |
| **TextBlob/VADER** | NLP情感分析 | ❌ 不需要 | 本地运行 |

**脚本位置:**
```
fincept-qt/scripts/fetch_company_news.py     # 公司新闻
fincept-qt/scripts/news_nlp.py               # NLP情感分析
fincept-qt/scripts/polymarket.py             # 预测市场
fincept-qt/scripts/reddit_sentiment.py       # Reddit情绪(需创建)
```

**配置Reddit API (免费):**
```python
# 1. 创建Reddit应用: https://www.reddit.com/prefs/apps
# 2. 获取 client_id 和 client_secret
# 3. 在脚本中配置:

import praw
reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="FinceptTerminal/1.0"
)
```

### 6. 另类数据 (Alternative Data)

#### 免费卫星与地理数据

| 数据源 | 数据类型 | API密钥 | 状态 |
|--------|---------|---------|------|
| **NASA GIBS** | 卫星影像 | ❌ 不需要 | ✅ 已集成 |
| **Sentinel Hub** | 哨兵卫星 | 需要(免费层) | ⚠️ 需配置 |
| **Copernicus** | 气候数据 | ❌ 不需要 | ✅ 已集成 |
| **NOAA** | 气象数据 | ❌ 不需要 | ✅ 已集成 |
| **MarineTraffic** | 船舶追踪 | 需要(免费层) | ⚠️ 需配置 |
| **AISstream** | AIS数据流 | 需要(免费) | ✅ 已集成 |

**脚本位置:**
```
fincept-qt/scripts/nasa_gibs_api.py          # NASA卫星
fincept-qt/scripts/sentinelhub_data.py       # Sentinel
fincept-qt/scripts/copernicus_data.py        # Copernicus
fincept-qt/scripts/noaa_climate_data.py      # NOAA
fincept-qt/scripts/marinetraffic_data.py     # MarineTraffic
fincept-qt/scripts/aisstream_data.py         # AISstream
```

---

## 🚀 新建: 完全免费的宏观数据聚合器

我已为您创建了 `free_macro_aggregator.py`,它聚合以下**完全免费**的数据源:

```python
# 使用方法
python free_macro_aggregator.py dashboard US    # 美国宏观仪表板
python free_macro_aggregator.py rates EU        # 欧洲央行政策利率
python free_macro_aggregator.py inflation CN    # 中国通胀数据
python free_macro_aggregator.py gdp GLOBAL      # 全球GDP数据
python free_macro_aggregator.py debt US         # 美国主权债务
python free_macro_aggregator.py emerging        # 新兴市场指标
```

**数据来源:**
- World Bank Open Data (完全免费)
- IMF Statistics (完全免费)
- FRED (可选API Key,无Key也可用)
- OECD Statistics (完全免费)
- AKShare China Macro (完全免费)
- ECB Statistical Data Warehouse (完全免费)
- BIS Statistics (完全免费)

**特点:**
- ✅ 零API密钥依赖(除可选FRED)
- ✅ 覆盖40+国家
- ✅ 包含利率、通胀、GDP、债务、新兴市场
- ✅ JSON输出,易于Qt/C++集成

---

## 💰 真实交易执行 (Real Trading)

### 券商API (多数免费)

| 券商 | 地区 | API费用 | 账户要求 |
|------|------|---------|---------|
| **Zerodha Kite** | 印度 | 免费 | 需要账户 |
| **Angel One** | 印度 | 免费 | 需要账户 |
| **Upstox** | 印度 | 免费 | 需要账户 |
| **Alpaca** | 美国 | 免费 | 需要账户 |
| **IBKR** | 全球 | 免费API | 需要账户+$0最小值 |
| **Binance** | 全球 | 免费 | 需要账户 |
| **Kraken** | 全球 | 免费 | 需要账户 |

**注意:** 券商API本身免费,但需要开通真实交易账户(这是券商的要求,不是Fincept收费)

### 模拟交易 (Paper Trading)
```
✅ 已内置完整模拟交易系统
✅ 无需任何费用
✅ 支持所有策略测试
```

---

## 📊 高频数据 (Tick Data)

### 免费方案

| 数据源 | 延迟 | API密钥 | 状态 |
|--------|------|---------|------|
| **Databento Free** | 实时 | 需要(免费) | ✅ 已集成 |
| **Yahoo Finance** | 15分钟 | ❌ 不需要 | ✅ 已集成 |
| **Binance WebSocket** | 实时 | ❌ 不需要 | ✅ 已集成 |
| **Kraken WebSocket** | 实时 | ❌ 不需要 | ✅ 已集成 |
| **Polygon.io Free** | 15分钟 | 需要(免费) | ⚠️ 需配置 |

**配置Databento (免费层):**
```python
# 注册: https://databento.com
# 免费层: 1GB数据/月,足够个人使用

# 在Fincept Terminal中配置
数据源 → Databento → 输入API Key
```

---

## 🎯 完全免费部署步骤

### 步骤1: 禁用Fincept API依赖

修改配置文件或环境变量:
```bash
# .env 文件或系统环境变量
FINCEPT_API_ENABLED=false
USE_FREE_SOURCES_ONLY=true
```

### 步骤2: 替换FinceptMacroPanel

将 `FinceptMacroPanel.cpp` 连接到新的免费聚合器:

```cpp
// 修改 on_fetch() 方法
void FinceptMacroPanel::on_fetch() {
    // 调用免费聚合器而非Fincept API
    QString script = "free_macro_aggregator.py";
    QStringList args = {"dashboard", selected_country_};
    
    PythonService::instance().run_script(script, args, [this](const QString& output) {
        parse_and_display(output);
    });
}
```

### 步骤3: 配置免费LLM

在设置界面添加默认免费提供商:
```cpp
// 默认使用Ollama (无需API Key)
LlmConfig default_config;
default_config.provider = "ollama";
default_config.model = "llama3.2";
default_config.base_url = "http://localhost:11434";
```

### 步骤4: 移除订阅检查

对于个人使用,可以注释掉付费检查:

```cpp
// src/auth/AuthManager.cpp
bool AuthManager::requires_paid_plan(const QString& feature) {
    // 原代码: 检查用户订阅状态
    // 修改为: 始终返回false (个人使用)
    Q_UNUSED(feature);
    return false;  // 所有功能免费开放
}
```

⚠️ **注意:** 此修改仅适用于个人学习使用。商业用途仍需遵守AGPL-3.0许可或购买商业许可。

---

## 📈 免费方案性能对比

| 功能 | 付费方案 | 免费方案 | 差距 |
|------|---------|---------|------|
| 股票数据 | Fincept API | Yahoo + AKShare | 无(免费更全) |
| 宏观数据 | Bloomberg | FRED + WB + IMF | 延迟1-2天 |
| AI推理 | GPT-4 | Llama 3 (本地) | 质量略低但免费 |
| 回测 | QuantConnect | Backtrader | 无差距 |
| 实时交易 | 付费经纪商 | Alpaca/IBKR免费API | 无差距 |
| 新闻情感 | RavenPack | Reddit + VADER | 精度略低 |
| 卫星数据 | Orbital Insight | NASA + Sentinel | 分辨率略低 |

**结论:** 对于个人投资者和研究者,**免费方案完全可以满足需求**,仅在机构级超低延迟和高精度方面有差距。

---

## 🔗 相关资源

### 免费API注册链接
- FRED API: https://fred.stlouisfed.org/docs/api/api_key.html
- Reddit API: https://www.reddit.com/prefs/apps
- NewsAPI: https://newsapi.org/register
- DeepSeek: https://platform.deepseek.com
- Groq: https://console.groq.com
- Databento: https://databento.com
- Sentinel Hub: https://apps.sentinel-hub.com/oauth-client

### 开源项目
- AKShare: https://github.com/akfamily/akshare
- Ollama: https://github.com/ollama/ollama
- Backtrader: https://github.com/mementum/backtrader
- QuantLib: https://github.com/lballabio/QuantLib
- PyPortfolioOpt: https://github.com/robertmartin8/PyPortfolioOpt

---

## ⚖️ 许可说明

**个人/教育使用:**
- ✅ 完全免费
- ✅ 可使用所有开源数据源
- ✅ 可修改代码自用
- ⚠️ 需遵守AGPL-3.0(如分发需开源)

**商业使用:**
- ❌ 需要商业许可 ($10,200/年)
- ❌ 使用Fincept专有数据/API需付费
- ✅ 但可自建完全免费版本(使用上述免费源)

---

## 📝 总结

**Fincept Terminal的商业付费部分100%可以替换为免费方案:**

1. ✅ **市场数据**: Yahoo Finance + AKShare (更强大)
2. ✅ **宏观数据**: FRED + World Bank + IMF (已创建聚合器)
3. ✅ **量化分析**: QuantLib + Backtrader (行业标准)
4. ✅ **AI智能体**: Ollama + DeepSeek (免费/本地)
5. ✅ **新闻情感**: Reddit + GDELT + VADER (开源)
6. ✅ **另类数据**: NASA + Sentinel + NOAA (政府免费)
7. ✅ **实时交易**: Alpaca/IBKR免费API (券商免费)
8. ✅ **回测系统**: Backtrader (完全免费)

**唯一需要付费的场景:**
- 机构级超低延迟数据(<1ms)
- 商业分发Fincept品牌产品
- 需要Fincept官方技术支持

**对于个人投资者、研究者、学生:**
🎉 **完全可以零成本使用全部功能!**
