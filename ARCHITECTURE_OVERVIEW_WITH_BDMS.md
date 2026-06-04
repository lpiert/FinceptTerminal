# Fincept Terminal 整体架构梳理

## 📋 目录
1. [现有架构概览](#现有架构概览)
2. [分层架构详解](#分层架构详解)
3. [核心模块说明](#核心模块说明)
4. [数据流向分析](#数据流向分析)
5. [BDMS集成方案](#bdms集成方案)
6. [技术栈对比](#技术栈对比)
7. [集成路线图](#集成路线图)

---

## 🏗️ 现有架构概览

### 系统架构图

```
┌───────────────────────────────────────────────────────────────────┐
│                         User Interface Layer                       │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Qt6 Widgets + Qt6 Charts                                   │  │
│  │  - Obsidian设计系统 (Bloomberg风格终端UI)                     │  │
│  │  - 实时数据可视化                                            │  │
│  │  - 原生平台渲染                                              │  │
│  └─────────────────────────────────────────────────────────────┘  │
├───────────────────────────────────────────────────────────────────┤
│                       Application Layer                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │  Screens  │  │ Services │  │  Trading │  │  MCP Integration │ │
│  │  (40+)   │  │ (Data)   │  │  Engine  │  │  (AI Tools)      │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │
├───────────────────────────────────────────────────────────────────┤
│                      Infrastructure Layer                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │  HTTP     │  │  SQLite  │  │ WebSocket│  │  Python Bridge   │ │
│  │(Qt Network)│(Qt Sql)   │  │(Qt WS)   │  │  (100+ scripts)  │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │
├───────────────────────────────────────────────────────────────────┤
│                       Platform Layer                               │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Qt6 Platform Abstraction                                   │  │
│  │  Windows (MSVC) / macOS (Clang) / Linux (GCC)              │  │
│  └─────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────┘
```

### 免费化改造后的增强层

```
┌───────────────────────────────────────────────────────────────────┐
│                    Free Mode Enhancement Layer                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Free Data Sources (Python Scripts)                         │  │
│  │  ├─ Yahoo Finance (yfinance)                                │  │
│  │  ├─ AKShare (China Market)                                  │  │
│  │  ├─ FRED/World Bank/IMF/OECD (Macro Data)                  │  │
│  │  ├─ Reddit Sentiment (PRAW)                                 │  │
│  │  └─ Rate Limiter (Token Bucket)                             │  │
│  └─────────────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Free AI Providers                                          │  │
│  │  ├─ Ollama (Local LLM)                                      │  │
│  │  ├─ DeepSeek (Free API)                                     │  │
│  │  └─ Groq (Free Tier)                                        │  │
│  └─────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────┘
```

---

## 📚 分层架构详解

### 1. UI层 (User Interface)

**位置:** `fincept-qt/src/screens/`, `fincept-qt/src/ui/`

**职责:**
- 用户交互界面渲染
- 事件捕获和分发
- 数据展示和可视化

**核心组件:**
```
screens/
├── auth/           # 认证相关 (Login, Register, Pricing)
├── dashboard/      # 主仪表板 (13个widget)
├── markets/        # 市场数据
├── economics/      # 经济数据 (含FinceptMacroPanel)
├── news/           # 新闻聚合
├── watchlist/      # 自选股管理
├── crypto_trading/ # 加密货币交易
├── profile/        # 用户资料 (无限信用点显示)
├── settings/       # 设置
├── docs/           # 文档 (含FREE MODE章节)
└── about/          # 关于 (含FREE MODE声明)

ui/
├── theme/          # 主题系统 (Obsidian设计)
├── widgets/        # 通用组件 (Card, SearchBar等)
├── tables/         # 数据表格
├── charts/         # 图表工厂
└── navigation/     # 导航栏、状态栏
```

**关键特性:**
- ✅ Screen/Service分离原则
- ✅ Qt信号槽机制解耦
- ✅ 响应式布局
- ✅ 深色/浅色主题切换

---

### 2. 应用层 (Application Layer)

**位置:** `fincept-qt/src/services/`, `fincept-qt/src/trading/`

#### 2.1 服务层 (Services)

**职责:**
- 业务逻辑处理
- 数据获取和缓存
- API调用封装

**核心服务:**
```cpp
services/
├── markets/MarketDataService.cpp    # 市场数据服务
├── economics/EconomicsService.cpp   # 经济数据服务
├── news/NewsService.cpp             # 新闻服务
├── agents/AgentService.cpp          # AI智能体服务
├── dbnomics/DBnomicsService.cpp     # DBnomics数据
├── geopolitics/GeopoliticsService.cpp
├── maritime/MaritimeService.cpp
└── gov_data/GovDataService.cpp
```

**服务模式示例:**
```cpp
// EconomicsService 执行Python脚本
EconomicsService::instance().execute(
    "free-macro",           // source_id
    "free_macro_aggregator.py", // script
    "dashboard",            // command
    {"US"},                 // args
    "request_id"            // request_id
);
```

#### 2.2 交易引擎 (Trading Engine)

**职责:**
- 订单管理
- 经纪商接口
- 模拟交易

**核心组件:**
```cpp
trading/
├── BrokerInterface.h          # 经纪商抽象接口
├── BrokerRegistry.cpp         # 经纪商注册表
├── ExchangeService.cpp        # 交易所连接
├── OrderMatcher.cpp           # 订单撮合引擎
├── PaperTrading.cpp           # 模拟交易
├── UnifiedTrading.cpp         # 统一交易门面
└── brokers/                   # 20+经纪商实现
    ├── ZerodhaBroker.h
    ├── IBKRBroker.h
    ├── AlpacaBroker.h
    └── ...
```

---

### 3. 基础设施层 (Infrastructure Layer)

**位置:** `fincept-qt/src/network/`, `fincept-qt/src/storage/`, `fincept-qt/src/python/`

#### 3.1 网络通信

```cpp
network/
├── http/HttpClient.cpp        # QNetworkAccessManager封装
└── websocket/WebSocketClient.cpp  # Qt6 WebSocket封装
```

**特性:**
- ✅ 自动重试机制
- ✅ 超时控制
- ✅ SSL/TLS支持
- ✅ 代理支持 (HTTP_PROXY/HTTPS_PROXY)

#### 3.2 数据存储

```cpp
storage/
├── sqlite/
│   ├── Database.cpp           # 主数据库
│   ├── CacheDatabase.cpp      # 缓存数据库
│   └── migrations/            # 版本迁移
├── cache/
│   ├── CacheManager.cpp       # 缓存管理器
│   └── TabSessionStore.cpp    # 标签页会话存储
├── secure/SecureStorage.cpp   # 加密凭证存储
└── repositories/              # 数据访问对象 (13个)
    ├── SettingsRepository.cpp
    ├── WatchlistRepository.cpp
    ├── ChatRepository.cpp
    └── ...
```

**数据库架构:**
```
Main Database (app.db)
├── users              # 用户信息
├── sessions           # 会话记录
├── settings           # 应用设置
├── watchlists         # 自选股
└── chat_history       # 聊天历史

Cache Database (cache.db)
├── market_data        # 市场数据缓存
├── news_articles      # 新闻缓存
└── economic_indicators # 经济指标缓存
```

#### 3.3 Python桥接

```cpp
python/
└── PythonRunner.cpp     # Python脚本执行器
```

**执行流程:**
```
C++ Service
    ↓
QProcess启动Python解释器
    ↓
执行 scripts/*.py
    ↓
脚本输出JSON到stdout
    ↓
C++解析QJsonDocument
    ↓
返回Result<T>
```

**免费模式Python脚本:**
```
scripts/
├── free_macro_aggregator.py    # 宏观数据聚合器
├── reddit_sentiment.py         # Reddit情感分析
├── api_rate_limiter.py         # API速率限制器
├── sentinel_config.py          # Sentinel配置助手
└── performance_benchmark.py    # 性能基准测试
```

---

### 4. 核心基础设施 (Core Infrastructure)

**位置:** `fincept-qt/src/core/`, `fincept-qt/src/auth/`

#### 4.1 核心模块

```cpp
core/
├── config/
│   ├── AppConfig.cpp          # 应用配置常量
│   ├── AppPaths.cpp           # 路径管理
│   └── ProfileManager.cpp     # 多配置文件管理
├── logging/Logger.cpp         # 结构化日志
├── events/EventBus.cpp        # 发布订阅总线
├── result/Result.h            # Result<T>错误处理
├── session/
│   ├── SessionManager.cpp     # 会话管理
│   └── ScreenStateManager.cpp # 屏幕状态管理
└── keys/KeyConfigManager.cpp  # 快捷键配置
```

#### 4.2 认证系统 (免费化改造重点)

```cpp
auth/
├── AuthManager.cpp            # 认证管理器 [已修改]
├── AuthTypes.h                # 认证类型 [已修改]
├── UserApi.cpp                # 用户API
└── SessionGuard.cpp           # 会话守卫
```

**免费模式改造:**
```cpp
// AuthTypes.h - has_paid_plan()
bool has_paid_plan() const {
    // [FREE-MODE-STUB] Always return true
    return true;  // 所有功能解锁
}

// AuthManager.cpp - complete_auth_flow()
session_.subscription.credit_balance = 999999;  // 无限信用点
session_.has_subscription = true;
```

---

## 🔄 数据流向分析

### 1. API数据流 (传统方式)

```
用户点击"获取AAPL报价"
        ↓
MarketsScreen (UI层)
        ↓ emit signal
MarketDataService (服务层)
        ↓
    ┌─── Option A: HTTP API
    │       ↓
    │   HttpClient → QNetworkAccessManager
    │       ↓
    │   Parse JSON (QJsonDocument)
    │
    └─── Option B: Python Script
            ↓
        PythonRunner → QProcess
            ↓
        scripts/market_data.py
            ↓
        stdout输出JSON
            ↓
        C++解析JSON
        ↓
emit signal with Result<T>
        ↓
MarketsScreen slot更新UI
```

### 2. 免费模式数据流 (新增)

```
用户选择国家"US"并点击"FETCH MACRO DATA"
        ↓
FinceptMacroPanel (UI层)
        ↓ emit signal
EconomicsService (服务层)
        ↓ execute()
PythonRunner → QProcess
        ↓
scripts/free_macro_aggregator.py
        ↓
调用多个免费API:
  ├─ World Bank API
  ├─ IMF Statistics
  ├─ FRED Economic Data
  ├─ OECD Statistics
  ├─ AKShare (China)
  ├─ ECB Data
  └─ BIS Statistics
        ↓
聚合数据为JSON
        ↓
stdout输出
        ↓
EconomicsService解析
        ↓ emit result_ready
FinceptMacroPanel::on_result()
        ↓
display() 显示表格数据
```

### 3. BDMS实时数据流 (待集成)

```
FinceptTerminal启动
        ↓
初始化BDMS MarketDataHub
        ↓
WebSocket连接到行情服务器
        ↓
订阅请求: subscribeRealtimeQuote("AAPL")
        ↓
RxCpp Observable创建
        ↓
实时数据推送:
  ├─ 实时报价 (RealtimeQuote)
  ├─ K线数据 (KLine)
  ├─ 分时数据 (MinuteLine)
  ├─ 成交明细 (TradeDetail)
  └─ 板块榜单 (BoardBank)
        ↓
ViewModel转换 (Converter)
        ↓
Qt信号发送到UI
        ↓
实时更新图表和表格
```

---

## 🔌 BDMS集成方案

### BDMS Market Data Center简介

**位置:** `D:\workspace\applyEnvQt6\code\libs\bdms-marketdatacenter`

**技术栈:**
- Qt6 (Core, Widgets, Network, WebSockets, Protobuf)
- RxCpp (响应式编程)
- Protobuf (数据序列化)
- C++17

**核心特性:**
- ✅ 实时行情数据流
- ✅ 响应式编程模型 (RxCpp)
- ✅ 智能缓存和回放
- ✅ 自动重连机制
- ✅ 线程安全分片锁

### 架构对比

| 维度 | Fincept Terminal | BDMS MarketData |
|------|------------------|-----------------|
| **数据源** | HTTP API + Python | WebSocket实时流 |
| **延迟** | 秒级 ( polling) | 毫秒级 (push) |
| **编程模型** | 信号槽 + Future | RxCpp Observable |
| **缓存策略** | SQLite + Memory | 多级缓存 + 回放 |
| **适用场景** | 低频查询、分析 | 高频交易、实时监控 |
| **依赖复杂度** | 中等 (Qt6 + Python) | 较高 (RxCpp + Protobuf) |

### 集成方案设计

#### 方案A: 可选数据源 (推荐) ⭐

**架构:**
```
┌────────────────────────────────────────────────┐
│           MarketDataService (统一入口)          │
├──────────────┬─────────────────────────────────┤
│  Default     │  Optional (BDMS)                │
│  Provider    │  Provider                       │
├──────────────┼─────────────────────────────────┤
│ • Yahoo      │ • Real-time Quotes              │
│ • AKShare    │ • K-line Data                   │
│ • FRED       │ • Minute Line                   │
│ • World Bank │ • Trade Details                 │
└──────────────┴─────────────────────────────────┘
         ↓
   Configuration File
   (config.json)
```

**实现步骤:**

1. **添加BDMS子模块**
```cmake
# fincept-qt/CMakeLists.txt
option(ENABLE_BDMS "Enable BDMS Market Data integration" OFF)

if(ENABLE_BDMS)
    add_subdirectory(${BDMS_PATH} bdms-marketdatacenter)
    target_link_libraries(FinceptTerminal PRIVATE marketdatacenter)
    target_compile_definitions(FinceptTerminal PRIVATE ENABLE_BDMS_INTEGRATION)
endif()
```

2. **创建BDMS适配器**
```cpp
// src/services/markets/BdmsMarketDataProvider.h
#ifdef ENABLE_BDMS_INTEGRATION
#include "MDC/api/subscribedatastream.h"

class BdmsMarketDataProvider : public IMarketDataProvider {
public:
    void initialize() override;
    Result<RealtimeQuote> getQuote(const QString& symbol) override;
    rxcpp::observable<RealtimeQuote> subscribeQuote(const QString& symbol) override;
    
private:
    bool m_initialized = false;
};
#endif
```

3. **配置管理**
```json
{
  "market_data": {
    "provider": "auto",  // "yahoo", "bdms", "auto"
    "bdms": {
      "enabled": false,
      "server_url": "ws://your-server:port",
      "format": "protobuf"
    }
  }
}
```

**优点:**
- ✅ 低耦合,可独立编译
- ✅ 用户可选择启用
- ✅ 不影响现有功能
- ✅ 易于测试和维护

**缺点:**
- ⚠️ 需要维护两套数据源
- ⚠️ 增加构建复杂度

---

#### 方案B: 插件化集成

**架构:**
```
FinceptTerminal.exe
    ↓ 动态加载
plugins/
├── yahoo_provider.dll      # Yahoo数据源插件
├── akshare_provider.dll    # AKShare插件
└── bdms_provider.dll       # BDMS插件 (可选)
```

**实现:**
```cpp
// Plugin接口
class IMarketDataPlugin {
public:
    virtual ~IMarketDataPlugin() = default;
    virtual QString name() const = 0;
    virtual void initialize() = 0;
    virtual Result<RealtimeQuote> getQuote(const QString& symbol) = 0;
};

// 插件加载器
class PluginManager {
public:
    void loadPlugins(const QString& pluginDir);
    IMarketDataPlugin* getProvider(const QString& name);
};
```

**优点:**
- ✅ 完全解耦
- ✅ 热插拔支持
- ✅ 独立版本管理

**缺点:**
- ❌ 开发成本高
- ❌ 调试复杂
- ❌ ABI兼容性问题

---

#### 方案C: 深度集成 (不推荐)

将BDMS代码直接合并到Fincept Terminal源码树中。

**缺点:**
- ❌ 高耦合
- ❌ 许可证冲突风险
- ❌ 维护困难

---

### 推荐实施方案: 方案A (渐进式)

**Phase 1: 基础集成 (2-3天)**
1. 编译BDMS库为DLL
2. 创建适配器接口
3. 添加配置选项
4. 实现基本行情获取

**Phase 2: 功能完善 (3-5天)**
1. 实现实时订阅
2. 添加错误处理
3. 编写单元测试
4. 性能优化

**Phase 3: UI集成 (2-3天)**
1. 创建BDMS设置页面
2. 添加实时行情面板
3. 集成到现有图表
4. 用户文档

**总工作量:** 约7-11天

---

## 🛠️ 技术栈对比

### 现有技术栈

| 组件 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 语言 | C++ | 20 | 核心应用 |
| UI框架 | Qt6 Widgets | 6.8.3 | 桌面GUI |
| 图表 | Qt6 Charts | 6.8.3 | 金融图表 |
| 网络 | Qt6 Network | 6.8.3 | HTTP/WebSocket |
| 数据库 | Qt6 Sql (SQLite) | 6.8.3 | 本地存储 |
| Python | CPython | 3.11+ | 数据分析脚本 |
| 构建 | CMake | 3.20+ | 跨平台构建 |
| 编译器 | MSVC/Clang/GCC | 最新 | 平台编译 |

### BDMS新增技术

| 组件 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 响应式编程 | RxCpp | 2.x | 数据流处理 |
| 序列化 | Protobuf | 3.x | 高效数据传输 |
| WebSocket | Qt6 WebSockets | 6.8.3 | 实时通信 |
| 缓存 | 自定义 | - | 多级缓存策略 |

### 兼容性评估

✅ **完全兼容:**
- Qt6版本一致 (6.8.3)
- C++标准兼容 (C++17 ⊂ C++20)
- 构建系统一致 (CMake)

⚠️ **需要注意:**
- RxCpp头文件库,需添加到include路径
- Protobuf需要预编译proto文件
- 可能需要调整编译选项 (`/bigobj` for MSVC)

---

## 🗺️ 集成路线图

### 短期目标 (1-2周)

**Week 1: 准备阶段**
- [ ] 确认BDMS许可证
- [ ] 编译BDMS库成功
- [ ] 运行BDMS测试程序
- [ ] 了解行情服务器地址和协议

**Week 2: 基础集成**
- [ ] 创建CMake集成配置
- [ ] 实现BDMS适配器接口
- [ ] 添加配置文件支持
- [ ] 实现基本行情获取功能

### 中期目标 (3-4周)

**Week 3: 功能开发**
- [ ] 实现实时订阅功能
- [ ] 集成到MarketDataService
- [ ] 添加错误处理和重试
- [ ] 编写单元测试

**Week 4: UI集成**
- [ ] 创建BDMS设置界面
- [ ] 添加实时行情显示面板
- [ ] 集成到现有图表组件
- [ ] 性能测试和优化

### 长期目标 (1-2月)

**高级功能:**
- [ ] 支持多种数据类型 (K线、分时、成交)
- [ ] 实现数据缓存和回放
- [ ] 添加离线模式支持
- [ ] 移动端适配考虑

**生态建设:**
- [ ] 编写完整文档
- [ ] 创建示例项目
- [ ] 社区反馈收集
- [ ] 持续优化和改进

---

## 📊 决策建议

### 是否集成BDMS?

**建议集成的场景:**
✅ 需要实时行情数据 (毫秒级延迟)  
✅ 目标用户包含专业交易者  
✅ 有稳定的行情服务器资源  
✅ 团队有C++和RxCpp经验  

**不建议集成的场景:**
❌ 仅需要低频数据查询  
❌ 目标用户为普通投资者  
❌ 没有行情服务器基础设施  
❌ 开发资源紧张  

### 替代方案

如果BDMS集成成本过高,可以考虑:

1. **WebSocket增强现有方案**
   - 使用免费的WebSocket行情源
   - 如: Binance WebSocket (crypto)
   - 如: Alpha Vantage WebSocket

2. **第三方SDK**
   - Polygon.io SDK
   - IEX Cloud SDK
   - Twelve Data SDK

3. **保持现状**
   - 继续使用Yahoo/AKShare
   - 优化Python脚本性能
   - 增加缓存命中率

---

## 🎯 下一步行动

### 立即执行

1. **确认需求**
   ```bash
   # 与产品团队确认
   - 是否需要实时行情?
   - 目标用户是谁?
   - 预算和时间约束?
   ```

2. **技术验证**
   ```bash
   # 编译BDMS测试
   cd D:\workspace\applyEnvQt6\code\libs\bdms-marketdatacenter
   cmake --build . --config Release
   
   # 运行测试程序
   .\Release\marketDataCenterTest.exe
   ```

3. **许可证审查**
   - 检查BDMS的LICENSE文件
   - 确认是否可以商用/开源使用
   - 咨询法务部门意见

### 决策后行动

**如果决定集成:**
- 按照路线图Phase 1开始实施
- 分配开发资源
- 制定详细计划

**如果暂不集成:**
- 记录决策原因
- 保留BDMS作为未来选项
- 继续优化现有数据源

---

## 📞 联系与支持

**技术问题:**
- GitHub Issues: https://github.com/Fincept-Corporation/FinceptTerminal/issues
- Email: support@fincept.in

**BDMS相关问题:**
- 查看BDMS README.md
- 联系BDMS维护团队

---

**文档版本:** 1.0  
**最后更新:** 2026-04-24  
**作者:** AI Assistant  
**审核状态:** 待审核  
