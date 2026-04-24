# UI团队并行开发指南 - 中国市场功能

本文档指导UI团队如何基于桩代码立即开始Level 2行情和交易界面的开发，无需等待后端API对接。

---

## 🎯 核心原则

**前后端分离开发**:
- ✅ 后端提供接口桩（Stub）和模拟数据
- ✅ UI基于桩代码开发完整界面
- ✅ 后续接入真实API时，UI代码无需修改

---

## 📦 已准备的UI组件

### 1. **OrderBookWidget** - Level 2十档行情

**文件位置**:
- `src/ui/widgets/OrderBookWidget.h`
- `src/ui/widgets/OrderBookWidget.cpp`

**功能**:
- 显示买卖十档行情
- 显示加权均价、买卖总量
- 每3秒自动刷新（模拟实时推送）

**使用方法**:

```cpp
#include "ui/widgets/OrderBookWidget.h"

// 在Dashboard或MarketPanel中创建
auto* order_book = new fincept::ui::OrderBookWidget(this);
order_book->set_symbol("600519.SS");  // 设置股票代码

// 添加到布局
layout->addWidget(order_book);
```

**当前行为**:
- 调用 `Level2DataService::get_depth()` 返回模拟数据
- 买盘价格略低于100元，卖盘价格略高于100元
- 成交量随机生成（10-1000手）

**UI开发重点**:
- ✅ 布局优化（表格对齐、字体大小）
- ✅ 颜色方案（买盘绿色、卖盘红色）
- ✅ 响应式设计（窗口缩放适配）
- ✅ 性能测试（大量数据渲染）

**后续对接**:
- 后端实现真实API后，UI自动接收真实数据
- **UI代码无需任何修改**

---

### 2. **TradingPanelWidget** - 交易下单面板

**文件位置**:
- `src/ui/widgets/TradingPanelWidget.h`
- `src/ui/widgets/TradingPanelWidget.cpp`

**功能**:
- 选择券商账户（CTP/XTP等）
- 输入股票代码、价格、数量
- 选择买卖方向、订单类型
- 显示可用资金、持仓信息
- 下单/撤单按钮

**使用方法**:

```cpp
#include "ui/widgets/TradingPanelWidget.h"

// 创建交易面板
auto* trading_panel = new fincept::ui::TradingPanelWidget(this);
trading_panel->set_symbol("600519.SS");
trading_panel->set_broker_id("ctp");  // 默认选择CTP

// 连接信号
connect(trading_panel, &fincept::ui::TradingPanelWidget::order_placed,
        this, [this](const QString& order_id) {
            LOG_INFO("Trading", QString("Order placed: %1").arg(order_id));
        });

connect(trading_panel, &fincept::ui::TradingPanelWidget::order_failed,
        this, [this](const QString& error) {
            QMessageBox::warning(this, "下单失败", error);
        });

// 添加到布局
layout->addWidget(trading_panel);
```

**当前行为**:
- 点击"下单"按钮会弹出提示框："这是桩代码演示..."
- 显示模拟的可用资金（¥1,000,000.00）
- A股数量验证（必须是100的整数倍）

**UI开发重点**:
- ✅ 表单布局优化（标签对齐、输入框宽度）
- ✅ 输入验证（价格范围、数量格式）
- ✅ 错误提示（友好消息、高亮错误字段）
- ✅ 状态反馈（加载中、成功、失败）
- ✅ 键盘快捷键（Enter下单、Esc取消）

**待完善功能**:
- [ ] 添加止盈止损输入框
- [ ] 添加高级订单类型（条件单、网格交易）
- [ ] 集成扫码登录（券商APP授权）

---

### 3. **FuturesRolloverAlertWidget** - 期货换月提示

**文件位置**:
- `src/ui/widgets/FuturesRolloverAlertWidget.h`
- `src/ui/widgets/FuturesRolloverAlertWidget.cpp`

**功能**:
- 监控主力合约到期状态
- 检测到需要换月时显示醒目横幅
- 提供"立即切换"和"稍后提醒"按钮

**使用方法**:

```cpp
#include "ui/widgets/FuturesRolloverAlertWidget.h"

// 创建换月提示组件
auto* rollover_alert = new fincept::ui::FuturesRolloverAlertWidget(this);

// 注册要监控的品种
rollover_alert->watch_contract("rb", "SHF");  // 螺纹钢
rollover_alert->watch_contract("IF", "CFX");  // 沪深300期指

// 连接信号
connect(rollover_alert, &fincept::ui::FuturesRolloverAlertWidget::rollover_confirmed,
        this, [this](const QString& symbol, const QString& old_c, const QString& new_c) {
            LOG_INFO("Futures", QString("Switching %1 from %2 to %3")
                                    .arg(symbol).arg(old_c).arg(new_c));
            // 更新UI显示的合约
            update_contract_display(new_c);
        });

// 添加到顶部布局
top_layout->addWidget(rollover_alert);
```

**当前行为**:
- 启动时检查一次换月状态
- 每小时自动检查一次
- 使用模拟到期日（合约月份15日）

**UI开发重点**:
- ✅ 横幅样式（渐变背景、圆角边框）
- ✅ 动画效果（滑入/滑出）
- ✅ 图标设计（警告符号）
- ✅ 按钮交互（hover效果、点击反馈）

---

## 🎨 设计规范

### 颜色方案

遵循Fincept Terminal的Obsidian主题：

| 元素 | 颜色 | 说明 |
|------|------|------|
| 背景色 | `#1e1e1e` | 深色背景 |
| 买盘价格 | `#00ff00` | 绿色 |
| 卖盘价格 | `#ff0000` | 红色 |
| 文字主色 | `#ffffff` | 白色 |
| 文字副色 | `#aaaaaa` | 灰色 |
| 强调色 | `#ffaa00` | 橙色（警告） |
| 按钮主色 | `#00aa00` | 绿色（买入） |
| 按钮危险色 | `#aa0000` | 红色（卖出/撤单） |

### 字体规范

```css
/* 标题 */
font-weight: bold;
font-size: 14px;
color: #ffffff;

/* 普通文本 */
font-size: 12px;
color: #cccccc;

/* 数字（价格、数量）*/
font-family: monospace;  /* 等宽字体对齐 */
font-size: 13px;
```

### 间距规范

```cpp
// 组件内边距
layout->setContentsMargins(12, 12, 12, 12);

// 组件间距
layout->setSpacing(8);

// 表格行列间距
grid_layout->setHorizontalSpacing(10);
grid_layout->setVerticalSpacing(2);
```

---

## 🧪 测试方法

### 1. 编译测试

确保新组件能成功编译：

```bash
cd build
cmake .. -DCMAKE_BUILD_TYPE=Debug
make -j$(nproc)
```

**常见问题**:
- ❌ 找不到头文件 → 检查 `CMakeLists.txt` 是否添加了新文件
- ❌ Qt MOC错误 → 确保类声明中有 `Q_OBJECT` 宏

### 2. 运行时测试

在主窗口中嵌入测试：

```cpp
// MainWindow.cpp 或 DashboardScreen.cpp
#include "ui/widgets/OrderBookWidget.h"
#include "ui/widgets/TradingPanelWidget.h"

void MyScreen::setup_test_ui() {
    auto* layout = new QVBoxLayout(this);

    // 测试OrderBookWidget
    auto* order_book = new fincept::ui::OrderBookWidget(this);
    order_book->set_symbol("600519.SS");
    layout->addWidget(order_book);

    // 测试TradingPanelWidget
    auto* trading_panel = new fincept::ui::TradingPanelWidget(this);
    trading_panel->set_symbol("600519.SS");
    layout->addWidget(trading_panel);

    setLayout(layout);
}
```

### 3. 模拟数据验证

**OrderBookWidget**:
- 应该显示10档买卖盘
- 买盘价格在95-99元之间
- 卖盘价格在101-105元之间
- 每3秒自动刷新

**TradingPanelWidget**:
- 点击"下单"应弹出提示框
- 输入非100倍数的数量应提示错误
- 下拉框应显示"CTP期货"和"XTP股票"选项

---

## 📋 UI开发任务清单

### Phase 1: 基础界面（1-2周）

#### OrderBookWidget
- [ ] 优化表格布局（列宽自适应）
- [ ] 添加买卖盘深度可视化（柱状图）
- [ ] 实现滚动查看50档行情（如果数据支持）
- [ ] 添加最后更新时间戳

#### TradingPanelWidget
- [ ] 完善输入验证（价格涨跌幅限制）
- [ ] 添加快速输入按钮（+100, -100, ×2, ÷2）
- [ ] 实现常用股票列表（双击填入）
- [ ] 添加下单确认对话框

#### FuturesRolloverAlertWidget
- [ ] 设计滑入/滑出动画
- [ ] 添加"不再提示此合约"选项
- [ ] 实现多合约同时提示（堆叠显示）

---

### Phase 2: 交互优化（1周）

#### 通用
- [ ] 添加加载动画（数据请求中）
- [ ] 实现错误重试机制
- [ ] 添加Tooltips提示
- [ ] 支持键盘导航（Tab键切换输入框）

#### OrderBookWidget
- [ ] 点击某档价格自动填入交易面板
- [ ] 鼠标悬停显示详细信息（委托笔数）
- [ ] 闪烁效果（价格变动时高亮）

#### TradingPanelWidget
- [ ] 记住上次输入的价格/数量
- [ ] 一键全仓/半仓/1/3仓按钮
- [ ] 实时计算手续费和预估盈亏

---

### Phase 3: 高级功能（2-3周）

#### Level 2可视化
- [ ] 买卖盘堆积图（横向柱状图）
- [ ] 逐笔成交流水（滚动列表）
- [ ] 大单提醒（成交量 > 1000手高亮）
- [ ] 买卖力道对比（饼图）

#### 交易增强
- [ ] 条件单设置（价格触发、时间触发）
- [ ] 网格交易配置
- [ ] 批量下单（多个股票同时下单）
- [ ] 订单管理面板（查看所有挂单）

#### 风控面板
- [ ] 实时风险度显示（期货保证金比例）
- [ ] 预警设置（价格预警、仓位预警）
- [ ] 强制平仓提示

---

## 🔗 与后端协作

### 接口约定

**Level 2数据格式**（已在 `Level2DataService.h` 定义）:
```cpp
struct Level2Depth {
    QString symbol;
    QVector<Level2Order> bids;  // 买盘10档
    QVector<Level2Order> asks;  // 卖盘10档
    double bid_weighted_avg;
    double ask_weighted_avg;
    qint64 total_bid_volume;
    qint64 total_ask_volume;
};
```

**UI团队无需关心**:
- 数据从哪里来（HTTP/WebSocket/SDK）
- 如何解析原始数据
- 如何处理网络错误

**UI团队只需调用**:
```cpp
auto& service = Level2DataService::instance();
auto result = service.get_depth("600519.SS");
if (result.is_ok()) {
    const auto& depth = result.value();
    // 使用depth渲染UI
}
```

---

### 联调时间表

| 阶段 | 时间 | 前端任务 | 后端任务 |
|------|------|---------|---------|
| Phase 1 | 第1-2周 | 基于桩代码开发UI | 保持桩代码稳定 |
| Phase 2 | 第3周 | UI优化和测试 | 开始对接真实API |
| Phase 3 | 第4周 | 准备联调环境 | 完成API对接 |
| Phase 4 | 第5周 | **联调测试** | 修复Bug |
| Phase 5 | 第6周 | 上线发布 | 监控稳定性 |

---

## 💡 常见问题

### Q1: 为什么点击"下单"没有真实下单？

**A**: 当前Broker是桩代码，所有方法都返回"Not Implemented"。这是预期行为，UI团队可以：
1. 继续开发界面布局和交互
2. 测试输入验证逻辑
3. 等待后端对接真实API（CTP/XTP）

---

### Q2: Level 2数据多久刷新一次？

**A**: 当前 `OrderBookWidget` 每3秒调用一次 `get_depth()` 获取模拟数据。后续接入真实API后：
- 改为WebSocket推送（实时更新）
- UI代码无需修改，只需后端改变数据源

---

### Q3: 如何测试期货换月提示？

**A**: 手动触发测试：
```cpp
// 在某个按钮点击事件中
auto& rollover_mgr = FuturesRolloverManager::instance();
emit rollover_mgr.on_rollover_detected("rb", "rb2405", "rb2410");
```

或者直接修改 `FuturesRolloverManager::should_rollover()` 让它始终返回 `true`。

---

### Q4: CMake编译时报错找不到新文件？

**A**: 需要在 `CMakeLists.txt` 中添加新文件：

```cmake
# 找到现有的UI widgets源文件列表
set(UI_WIDGETS_SOURCES
    src/ui/widgets/Card.cpp
    src/ui/widgets/SearchBar.cpp
    # ... 其他文件
    src/ui/widgets/OrderBookWidget.cpp        # 新增
    src/ui/widgets/TradingPanelWidget.cpp     # 新增
    src/ui/widgets/FuturesRolloverAlertWidget.cpp  # 新增
)

# 同样添加头文件到 HEADERS 列表
```

---

## 📞 联系方式

遇到问题时的求助渠道：

1. **后端接口问题**: 查看 `CHINA_MARKET_TODO.md`
2. **UI组件问题**: 查看各组件头文件中的注释
3. **项目Issues**: https://github.com/Fincept-Corporation/FinceptTerminal/issues

---

**最后更新**: 2026-04-20  
**版本**: v1.0 (UI并行开发指南)

**祝开发顺利！** 🚀
