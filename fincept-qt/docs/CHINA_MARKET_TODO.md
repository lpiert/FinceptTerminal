# 中国市场拓展 - 后续开发TODO

本文档列出中国市场接入的待办事项，按优先级排序。

---

## ✅ 已完成 (Phase 1)

- [x] AkShare数据接口集成
- [x] A股/港股/期货/ETF行情支持
- [x] DataHub路由逻辑
- [x] 默认观察列表
- [x] 基础文档

---

## 🚧 进行中 (Phase 2)

### 2.1 Level 2 深度行情（付费接口）

**状态**: 已打桩，待对接

**文件**:
- `src/services/markets/Level2DataService.h`
- `src/services/markets/Level2DataService.cpp`

**待办**:
- [ ] 选择数据供应商（Wind/Choice/聚宽/Tushare Pro）
- [ ] 申请API密钥
- [ ] 实现HTTP/WebSocket客户端
- [ ] 解析Level 2数据格式（十档行情、逐笔成交）
- [ ] 集成到UI（Order Book Widget）

**推荐供应商对比**:

| 供应商 | 价格 | 数据质量 | API类型 | 适用对象 |
|--------|------|---------|---------|---------|
| Wind资讯 | ¥50k+/年 | 机构级 | C++/Python SDK | 机构 |
| EastMoney Choice | ¥5k/年 | 良好 | HTTP API | 个人/小机构 |
| 聚宽JoinQuant | 免费~¥3k/年 | 良好 | Python API | 量化开发者 |
| Tushare Pro | 积分制 | 中等 | HTTP API | 个人开发者 |
| 米筐RiceQuant | ¥2k/年 | 良好 | Python API | 量化开发者 |

**示例代码**（Tushare Pro）:
```python
import tushare as ts

# 设置token
ts.set_token('your_tushare_token')
pro = ts.pro_api()

# 获取Level 2十档行情
df = pro.l2_daily(ts_code='600519.SH', trade_date='20240420')

# 获取逐笔成交
df_ticks = pro.l2_tick(ts_code='600519.SH', start_time='093000', end_time='093500')
```

---

### 2.2 期货合约自动换月

**状态**: 已打桩，待完善

**文件**:
- `src/trading/FuturesRolloverManager.h`
- `src/trading/FuturesRolloverManager.cpp`

**待办**:
- [ ] 实现真实的主力合约判断逻辑（基于成交量/持仓量）
- [ ] 从交易所获取合约到期日
- [ ] 添加定时器，每日检查换月
- [ ] UI提示用户换月
- [ ] 支持自动换月配置

**实现思路**:
```cpp
// 在 MarketDataService 中定期检查
void MarketDataService::check_futures_rollover() {
    auto& rollover_mgr = FuturesRolloverManager::instance();

    // 注册需要监控的品种
    rollover_mgr.register_callback("rb", [this](const QString& old_c, const QString& new_c) {
        LOG_INFO("Futures", QString("Rollover: %1 -> %2").arg(old_c).arg(new_c));
        // 通知UI更新
        emit futures_contract_changed("rb", new_c);
    });

    // 每日检查
    QTimer* timer = new QTimer(this);
    connect(timer, &QTimer::timeout, []() {
        FuturesRolloverManager::instance().check_all_contracts();
    });
    timer->start(24 * 60 * 60 * 1000);  // 每天检查一次
}
```

---

## 📋 待开发 (Phase 3)

### 3.1 实盘交易接口 - CTP（期货）

**状态**: 已打桩，待对接

**文件**:
- `src/trading/brokers/CtpBroker.h`
- `src/trading/brokers/CtpBroker.cpp`

**前置要求**:
- [ ] 在期货公司开通程序化交易权限
- [ ] 签署风险揭示书
- [ ] 准备50万以上资产证明
- [ ] 通过仿真交易测试

**对接步骤**:

1. **下载CTP API**
   ```bash
   # 从上期技术官网下载
   # http://www.sfit.com.cn/5_2_DocumentDown.htm
   ```

2. **编译CTP动态库**
   ```cmake
   # CMakeLists.txt 中添加
   find_library(CTP_TRADER_API thosttraderapi)
   find_library(CTP_MD_API thostmduserapi)
   target_link_libraries(FinceptTerminal ${CTP_TRADER_API} ${CTP_MD_API})
   ```

3. **实现SPI回调**
   ```cpp
   class CtpTraderSpi : public CThostFtdcTraderSpi {
   public:
       void OnRspUserLogin(CThostFtdcRspUserLoginField* pRspUserLogin,
                          CThostFtdcRspInfoField* pRspInfo,
                          int nRequestID, bool bIsLast) override {
           if (pRspInfo->ErrorID == 0) {
               LOG_INFO("CTP", "Login successful");
           } else {
               LOG_ERROR("CTP", QString("Login failed: %1").arg(pRspInfo->ErrorMsg));
           }
       }

       void OnRtnOrder(CThostFtdcOrderField* pOrder) override {
           // 处理报单回报
       }

       void OnRtnTrade(CThostFtdcTradeField* pTrade) override {
           // 处理成交回报
       }
   };
   ```

4. **初始化并登录**
   ```cpp
   void CtpBroker::initialize() {
       m_trader_api = CThostFtdcTraderApi::CreateFtdcTraderApi("./flow/");
       CtpTraderSpi* spi = new CtpTraderSpi();
       m_trader_api->RegisterSpi(spi);
       m_trader_api->SubscribePrivateTopic(THOST_TERT_RESTART);
       m_trader_api->SubscribePublicTopic(THOST_TERT_RESTART);
       m_trader_api->RegisterFront("tcp://180.168.146.187:10130");  // 仿真环境
       m_trader_api->Init();
   }
   ```

5. **下单**
   ```cpp
   OrderPlaceResponse CtpBroker::place_order(const BrokerCredentials& creds,
                                              const UnifiedOrder& order) {
       CThostFtdcInputOrderField req;
       memset(&req, 0, sizeof(req));

       strcpy(req.BrokerID, creds.api_key.toStdString().c_str());
       strcpy(req.InvestorID, creds.user_id.toStdString().c_str());
       strcpy(req.InstrumentID, order.symbol.toStdString().c_str());
       req.Direction = (order.side == OrderSide::Buy) ? THOST_FTDC_D_Buy : THOST_FTDC_D_Sell;
       req.CombOffsetFlag[0] = map_product_type(order.product);
       req.VolumeTotalOriginal = static_cast<int>(order.quantity);
       req.LimitPrice = order.price;
       req.OrderPriceType = THOST_FTDC_OPT_LimitPrice;

       int ret = m_trader_api->ReqOrderInsert(&req, ++request_id);
       if (ret == 0) {
           return {true, "", ""};
       } else {
           return {false, "", QString("Order failed: %1").arg(ret)};
       }
   }
   ```

**参考资源**:
- 官方文档: http://www.sfit.com.cn/5_2_DocumentDown.htm
- GitHub示例: https://github.com/nicai0609/PythonCTP
- C++封装: https://github.com/krenn1994/ctp-wrapper

---

### 3.2 实盘交易接口 - XTP（A股）

**状态**: 已打桩，待对接

**文件**:
- `src/trading/brokers/XtpBroker.h`
- `src/trading/brokers/XtpBroker.cpp`

**前置要求**:
- [ ] 在中泰证券或合作券商开户
- [ ] 准备100万以上资产
- [ ] 签署程序化交易协议
- [ ] 通过仿真测试

**对接步骤**:

1. **下载XTP API**
   ```bash
   # 从XTP官网申请
   # https://xtp.zts.com.cn/
   ```

2. **初始化API**
   ```cpp
   void XtpBroker::initialize() {
       m_trader_api = XTP::API::TraderApi::CreateTraderApi(1, XTP_LOG_LEVEL_DEBUG);
       XtpTraderSpi* spi = new XtpTraderSpi();
       m_trader_api->RegisterSpi(spi);
       m_trader_api->SetSoftwareKey("your_software_key");

       int ret = m_trader_api->Login(ip, port, user, password, sock_type);
       if (ret == 0) {
           LOG_INFO("XTP", "Login successful");
       }
   }
   ```

3. **下单**
   ```cpp
   OrderPlaceResponse XtpBroker::place_order(const BrokerCredentials& creds,
                                              const UnifiedOrder& order) {
       XTPTradeParam param;
       memset(&param, 0, sizeof(param));

       param.market = map_exchange(order.exchange);
       strcpy(param.ticker, order.symbol.toStdString().c_str());
       param.price = order.price;
       param.quantity = order.quantity;
       param.side = (order.side == OrderSide::Buy) ? XTP_SIDE_BUY : XTP_SIDE_SELL;
       param.order_type = map_order_type(order.type);

       uint64_t order_id = m_trader_api->InsertOrder(param);
       return {true, QString::number(order_id), ""};
   }
   ```

**参考资源**:
- 官方文档: https://xtp.zts.com.cn/helpcenter.html
- GitHub示例: https://github.com/uforce-michael/xtp-trader

---

### 3.3 A股交易规则引擎

**待办**:
- [ ] 实现T+1交易限制检查
- [ ] 实现涨跌停板检查（±10% / ±20%）
- [ ] 实现最小交易单位检查（100股整数倍）
- [ ] 实现ST股票特殊规则（±5%）
- [ ] 实现科创板/创业板权限检查

**示例代码**:
```cpp
class ChinaTradingRules {
public:
    Result<void> validate_order(const UnifiedOrder& order,
                                 const QuoteData& current_quote) {
        // T+1检查
        if (!can_sell_today(order.symbol, order.side)) {
            return Err("T+1 rule: Cannot sell stocks bought today");
        }

        // 涨跌停检查
        double limit_up = current_quote.previous_close * 1.10;
        double limit_down = current_quote.previous_close * 0.90;
        if (order.price > limit_up || order.price < limit_down) {
            return Err("Price exceeds limit up/down");
        }

        // 最小交易单位检查
        if (static_cast<int>(order.quantity) % 100 != 0) {
            return Err("Quantity must be multiple of 100 shares");
        }

        return Ok();
    }

private:
    bool can_sell_today(const QString& symbol, OrderSide side) {
        // 查询今日买入记录
        // 如果是卖出且今日买入过，返回false
        return true;
    }
};
```

---

## 🔮 未来规划 (Phase 4)

### 4.1 量化策略回测框架

- [ ] 集成Backtrader或Zipline
- [ ] 支持A股历史数据回测
- [ ] 支持期货主力合约连续数据
- [ ] 提供策略模板（均线交叉、MACD、布林带等）

### 4.2 智能选股器

- [ ] 基于财务指标选股（PE/PB/ROE）
- [ ] 基于技术指标选股（RSI/MACD/MA）
- [ ] 基于资金流向选股
- [ ] 支持自定义筛选条件

### 4.3 风险监控面板

- [ ] 实时监控股票异常波动
- [ ] 监控账户风险度（期货保证金比例）
- [ ] 设置预警通知（短信/邮件/推送）
- [ ] 自动生成风险报告

---

## 📝 开发注意事项

### 1. 合规性

- ⚠️ **程序化交易报备**: 根据证监会规定，程序化交易者需向交易所报备
- ⚠️ **风控要求**: 必须实现事前风控（资金检查、持仓限制）
- ⚠️ **日志审计**: 所有交易指令需留存日志，保存至少20年

### 2. 性能优化

- 使用连接池管理CTP/XTP连接
- 行情数据采用增量更新，避免全量刷新
- Level 2数据量大，考虑使用环形缓冲区

### 3. 错误处理

- CTP/XTP API可能返回异步错误，需在SPI回调中处理
- 网络断开后自动重连
- 订单状态同步（本地与柜台一致性）

---

## 📞 联系与支持

遇到问题时的求助渠道：

1. **CTP技术支持**: support@sfit.com.cn
2. **XTP技术支持**: xtp_support@zts.com.cn
3. **AkShare社区**: https://github.com/akfamily/akshare/issues
4. **本项目Issues**: https://github.com/Fincept-Corporation/FinceptTerminal/issues

---

**最后更新**: 2026-04-20  
**版本**: v1.0 (Phase 1完成，Phase 2打桩完成)
