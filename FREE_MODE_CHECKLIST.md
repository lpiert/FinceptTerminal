# Fincept Terminal 免费化改造清单

## 📋 改造概览

本文档记录将Fincept Terminal从商业付费模式改造为完全免费版本的进度清单。

**改造原则:**
- ✅ 已完成的免费替换
- 🔨 待处理的付费功能(已打桩预留)
- ⚠️ 需要后续解决的问题

---

## ✅ 已完成免费替换

### 1. 认证与订阅系统

#### 1.1 订阅检查绕过
**文件:** `src/auth/AuthTypes.h`
**修改:** `has_paid_plan()` 方法
```cpp
// [FREE-MODE-STUB] Always return true to unlock all features
bool has_paid_plan() const {
    return true;  // Free mode: all features unlocked
}
```
**状态:** ✅ 完成
**影响:** 所有功能模块不再检查付费状态

#### 1.2 订阅API调用跳过
**文件:** `src/auth/AuthManager.cpp`
**修改:** `complete_auth_flow()` 方法
```cpp
// [FREE-MODE-STUB] Skip subscription API call - unlock all features for free
session_.subscription.credit_balance = 999999;  // Unlimited credits
session_.user_info.credit_balance = 999999;
```
**状态:** ✅ 完成
**影响:** 
- 不再调用UserApi获取订阅信息
- 信用点设置为999999(无限)
- 账户类型设为"free"

---

### 2. 数据源替换

#### 2.1 宏观经济数据聚合器
**文件:** `scripts/free_macro_aggregator.py` (新建)
**功能:** 聚合7个免费数据源
- World Bank Open Data
- IMF Statistics  
- FRED (Federal Reserve)
- OECD Statistics
- AKShare China Macro
- ECB Statistical Data Warehouse
- BIS Statistics

**状态:** ✅ 完成
**使用方式:**
```bash
python free_macro_aggregator.py dashboard US
python free_macro_aggregator.py rates EU
python free_macro_aggregator.py inflation CN
```

#### 2.2 市场数据源(已内置)
**已有免费脚本:**
- ✅ `yfinance_data.py` - Yahoo Finance (全球股票)
- ✅ `akshare_*.py` - AKShare (中国金融,40+脚本)
- ✅ `baostock_data.py` - BaoStock (A股历史)
- ✅ `coingecko.py` - CoinGecko (加密货币)
- ✅ `frankfurter_data.py` - Frankfurter (汇率)

**状态:** ✅ 已完成,无需改动

#### 2.3 量化分析工具(已内置)
**已有开源库:**
- ✅ QuantLib (衍生品定价,18模块)
- ✅ Backtrader (策略回测)
- ✅ PyPortfolioOpt (组合优化)
- ✅ TA-Lib/talipp (技术指标)
- ✅ Statsmodels (统计分析)

**状态:** ✅ 已完成,无需改动

---

### 3. AI智能体配置

#### 3.1 多LLM提供商支持(已内置)
**代码位置:** `src/screens/settings/LlmConfigSection.cpp`
**支持的免费提供商:**
- ✅ Ollama (本地运行,完全免费)
- ✅ DeepSeek (免费API额度)
- ✅ Groq (免费层)
- ✅ HuggingFace Transformers

**状态:** ✅ 已支持,用户需自行配置

**推荐配置:**
```bash
# 安装Ollama
ollama pull llama3.2  # 或 mistral, qwen2.5

# 在Fincept Terminal设置中:
# AI配置 → Provider: Ollama → Model: llama3.2
```

---

## 🔨 待处理功能(已打桩预留)

### 4. 需要手动配置的模块

#### 4.1 FinceptMacroPanel改造
**文件:** `src/screens/economics/panels/FinceptMacroPanel.cpp`
**当前状态:** 显示"Coming Soon"
**TODO:** 连接到`free_macro_aggregator.py`

**打桩位置:**
```cpp
void FinceptMacroPanel::on_fetch() {
    // TODO: [FREE-MODE] Connect to free_macro_aggregator.py
    // Current: show_empty("Fincept Macro data script is not yet available");
    // Should call: PythonService::run_script("free_macro_aggregator.py", args)
}
```

**优先级:** 🔴 高
**预计工作量:** 2小时

---

#### 4.2 新闻情感分析增强
**文件:** 需创建 `scripts/reddit_sentiment.py`
**当前状态:** 基础NLP已存在(`news_nlp.py`)
**TODO:** 添加Reddit/X社交媒体情绪

**打桩建议:**
```python
# scripts/reddit_sentiment.py (待创建)
"""
Reddit Sentiment Analysis
TODO: Configure Reddit API credentials
Register at: https://www.reddit.com/prefs/apps
"""
import praw

# [STUB] Replace with your credentials
reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",      # TODO: User config
    client_secret="YOUR_SECRET",     # TODO: User config  
    user_agent="FinceptTerminal/1.0"
)
```

**优先级:** 🟡 中
**预计工作量:** 4小时

---

#### 4.3 卫星数据配置
**文件:** `scripts/sentinelhub_data.py`
**当前状态:** 需要API密钥
**TODO:** 引导用户注册Sentinel Hub免费账户

**打桩建议:**
```python
# [STUB] Sentinel Hub Configuration
# Register free account: https://apps.sentinel-hub.com/oauth-client
# Free tier: 1000 units/month (enough for personal use)

INSTANCE_ID = os.environ.get('SENTINEL_INSTANCE_ID', '')
CLIENT_ID = os.environ.get('SENTINEL_CLIENT_ID', '')
CLIENT_SECRET = os.environ.get('SENTINEL_CLIENT_SECRET', '')

if not INSTANCE_ID:
    print("Warning: Sentinel Hub not configured")
    print("See: FREE_ALTERNATIVES_GUIDE.md for setup instructions")
```

**优先级:** 🟢 低
**预计工作量:** 1小时

---

### 5. 需要移除的商业逻辑

#### 5.1 PricingScreen保留但标记
**文件:** `src/screens/auth/PricingScreen.cpp`
**当前状态:** 显示付费套餐
**TODO:** 添加"Free Mode Active"提示

**建议修改:**
```cpp
void PricingScreen::build_ui() {
    // [FREE-MODE] Add banner indicating free mode
    auto* banner = new QLabel("🎉 FREE MODE ACTIVE - All Features Unlocked");
    banner->setStyleSheet("color: green; font-weight: bold;");
    vl->insertWidget(0, banner);
    
    // Keep existing pricing UI for reference
    // Users can still view plans but everything is free
}
```

**优先级:** 🟢 低
**原因:** 保留UI供参考,但不强制

---

#### 5.2 ProfileScreen信用点显示
**文件:** `src/screens/profile/ProfileScreen.cpp`
**当前状态:** 显示真实信用点余额
**TODO:** 显示"Unlimited"而非具体数字

**建议修改:**
```cpp
void ProfileScreen::update_session_display() {
    // [FREE-MODE] Show unlimited credits
    if (s.user_info.credit_balance >= 999999) {
        ov_credits_big_->setText("∞");
        credits_badge_->setText("UNLIMITED");
    } else {
        // Original logic
    }
}
```

**优先级:** 🟢 低
**原因:**  cosmetic改进

---

### 6. 文档与帮助系统

#### 6.1 免费使用指南
**文件:** `FREE_ALTERNATIVES_GUIDE.md` (已创建)
**内容:** 
- ✅ 完整免费替代方案说明
- ✅ 配置步骤
- ✅ API注册链接
- ✅ 性能对比

**状态:** ✅ 完成

#### 6.2 应用内帮助更新
**文件:** `src/screens/docs/DocsScreen.cpp`
**TODO:** 添加"Free Mode Guide"章节

**建议添加:**
```cpp
// In DocsScreen::build_sidebar()
add_doc_section("FREE MODE GUIDE", {
    "OVERVIEW", "How to use Fincept Terminal completely free",
    "DATA SOURCES", "All free data sources and how to configure them",
    "AI SETUP", "Configure Ollama/DeepSeek for free AI",
    "TROUBLESHOOTING", "Common issues in free mode"
});
```

**优先级:** 🟡 中
**预计工作量:** 3小时

---

## ⚠️ 仍需解决的问题

### 7. 商业许可合规性

#### 7.1 AGPL-3.0许可证要求
**问题:** 如果分发修改后的版本,必须开源
**解决方案:**
- ✅ 个人使用: 无限制
- ⚠️ 分发他人: 需遵守AGPL-3.0(开源修改)
- ❌ 商业分发: 需购买商业许可($10,200/年)

**打桩建议:**
```cpp
// src/app/MainWindow.cpp - About dialog
// [LEGAL] Add license notice
QString license_text = R"(
This modified version uses free data sources only.

For personal/educational use: Free under AGPL-3.0
For commercial distribution: Contact support@fincept.in

Original Fincept Terminal © Fincept Corporation
)";
```

**状态:** ⚠️ 需注意
**行动:** 在About对话框添加声明

---

### 8. 数据质量差异

#### 8.1 延迟对比
| 数据类型 | 付费方案 | 免费方案 | 差距 |
|---------|---------|---------|------|
| 股票价格 | 实时 | 15分钟(Yahoo) | ⚠️ 中等 |
| 宏观数据 | T+0 | T+1~2天 | ⚠️ 可接受 |
| 加密货币 | 实时 | 实时 | ✅ 无差距 |
| 新闻 | 实时 | 5-10分钟 | ⚠️ 轻微 |

**影响评估:**
- ✅ 个人投资者: 完全可接受
- ⚠️ 日内交易者: 可能需要付费实时数据
- ❌ 高频交易: 必须付费

**建议:** 在文档中明确说明延迟差异

---

### 9. API速率限制

#### 9.1 免费API限制汇总
| API | 免费限额 | 是否足够 |
|-----|---------|---------|
| FRED | 120次/分钟 | ✅ 充足 |
| World Bank | 无明确限制 | ✅ 充足 |
| Reddit | 100次/分钟 | ✅ 充足 |
| NewsAPI | 100次/天 | ⚠️ 有限 |
| DeepSeek | $2免费额度 | ✅ 数月 |
| Groq | 30次/分钟 | ✅ 充足 |

**打桩建议:**
```python
# scripts/api_rate_limiter.py (待创建)
"""
API Rate Limiter for Free Tier Services
Track usage and warn when approaching limits
"""

class RateLimiter:
    def __init__(self):
        self.usage = {}
    
    def check_limit(self, api_name: str) -> bool:
        # [STUB] Implement rate tracking
        # Warn user when approaching free tier limits
        pass
```

**优先级:** 🟡 中
**预计工作量:** 3小时

---

## 📊 改造进度统计

### 总体进度
```
✅ 已完成: 40% (核心功能免费化)
🔨 待处理: 45% (需配置和优化)  
⚠️ 需注意: 15% (许可和限制)
```

### 按模块分类
| 模块 | 完成度 | 备注 |
|------|--------|------|
| 认证系统 | 100% | 订阅检查已绕过 |
| 市场数据 | 100% | 免费源已内置 |
| 宏观数据 | 80% | 聚合器已创建,面板待连接 |
| 量化分析 | 100% | 开源库已集成 |
| AI智能体 | 70% | 多提供商支持,需用户配置 |
| 新闻情感 | 50% | 基础NLP完成,社交待添加 |
| 另类数据 | 60% | 卫星/航运需配置API |
| 交易系统 | 90% | 模拟交易完成,券商需账户 |
| 文档帮助 | 70% | 指南已创建,应用内待更新 |

---

## 🎯 下一步行动计划

### Phase 1: 核心功能完善 (1-2天)
1. ✅ ~~订阅检查绕过~~ (已完成)
2. 🔨 连接FinceptMacroPanel到free_macro_aggregator
3. 🔨 添加PricingScreen免费模式提示
4. 🔨 更新ProfileScreen显示无限信用点

### Phase 2: 数据源增强 (2-3天)
5. 🔨 创建Reddit情感分析脚本
6. 🔨 添加API速率限制器
7. 🔨 配置Sentinel Hub免费账户指南
8. 🔨 测试所有免费数据源稳定性

### Phase 3: 文档与UX (1-2天)
9. 🔨 更新DocsScreen添加免费模式章节
10. 🔨 在About对话框添加许可声明
11. 🔨 创建快速开始指南(视频/截图)
12. 🔨 编写故障排除FAQ

### Phase 4: 测试与优化 (2-3天)
13. 🔨 端到端测试所有功能
14. 🔨 性能基准测试(对比付费版)
15. 🔨 收集用户反馈
16. 🔨 优化慢速数据源缓存策略

---

## 🔧 技术债务清单

### 需要重构的代码
1. **AuthManager** - 分离免费/商业逻辑到不同类
2. **DataSourceRegistry** - 标记哪些是免费/付费源
3. **CreditSystem** - 改为可选(免费版禁用)
4. **UpdateChecker** - 避免检查商业更新

### 需要添加的配置项
```ini
# config/free_mode.ini (待创建)
[General]
free_mode_enabled=true
skip_subscription_check=true
unlimited_credits=true

[DataSources]
prefer_free_sources=true
fallback_to_paid=false

[AI]
default_provider=ollama
default_model=llama3.2
```

---

## 📝 用户迁移指南

### 从付费版切换到免费版

**步骤1: 备份配置**
```bash
cp ~/.config/FinceptTerminal/config.ini config_backup.ini
```

**步骤2: 重新编译(应用免费补丁)**
```bash
cd fincept-qt/build
cmake --build . --target clean
cmake --build .
```

**步骤3: 配置免费数据源**
```bash
# 安装Ollama (AI)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2

# 注册免费API (可选,提高限额)
# - FRED: https://fred.stlouisfed.org/docs/api/api_key.html
# - Reddit: https://www.reddit.com/prefs/apps
# - NewsAPI: https://newsapi.org/register
```

**步骤4: 验证免费模式**
```
启动Fincept Terminal
→ 登录(任意账户或本地模式)
→ 查看顶部栏: 应显示 "FREE | CR ∞"
→ 访问任何功能: 不应有付费提示
```

---

## 🆘 常见问题

### Q1: 免费版的性能如何?
**A:** 对于个人投资者和研究者,免费版性能完全足够。仅在超低延迟(<1ms)场景有差距。

### Q2: 是否需要API密钥?
**A:** 大部分免费源无需密钥。部分(如FRED、Reddit)提供可选密钥以提高限额。

### Q3: 可以商用免费版吗?
**A:** 个人公司内部使用可以。但分发产品给他人需遵守AGPL-3.0或购买商业许可。

### Q4: 数据准确性如何?
**A:** 免费源来自官方机构(World Bank、IMF、各国央行),准确性与付费版相同,仅延迟略高。

### Q5: 如何恢复到付费版?
**A:** 撤销`AuthTypes.h`和`AuthManager.cpp`的修改,重新编译即可。

---

## 📞 支持与反馈

**问题报告:** GitHub Issues
**讨论区:** GitHub Discussions  
**邮件:** (自建社区支持)

**注意:** 免费版不提供官方技术支持,依靠社区互助。

---

**最后更新:** 2026-04-20
**维护者:** Community
**许可证:** AGPL-3.0 (修改版)
