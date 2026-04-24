#pragma once
#include "trading/BrokerInterface.h"
#include <QString>

namespace fincept::trading {

/// CTP Broker Implementation - STUB
///
/// TODO: 对接上期技术CTP API
///
/// CTP (Comprehensive Trading Platform) 是中国期货市场标准的交易接口
/// 由上海期货信息技术有限公司开发，被国内所有期货公司采用
///
/// 官方文档: http://www.sfit.com.cn/
/// GitHub示例: https://github.com/nicai0609/PythonCTP
///
/// 接入要求:
/// 1. 需要期货公司开通程序化交易权限
/// 2. 需要签署风险揭示书
/// 3. 通常需要50万以上资产证明
/// 4. 需要通过仿真交易测试
///
/// 当前实现: 桩代码，返回"Not Implemented"
class CtpBroker : public IBroker {
public:
    CtpBroker();
    ~CtpBroker() override = default;

    // IBroker interface
    BrokerId id() const override { return "ctp"; }
    const char* name() const override { return "CTP (China Futures)"; }
    const char* base_url() const override { return ""; }  // CTP使用直连IP

    BrokerProfile profile() const override;

    TokenExchangeResponse exchange_token(const QString& api_key, const QString& api_secret,
                                         const QString& auth_code) override;

    OrderPlaceResponse place_order(const BrokerCredentials& creds,
                                   const UnifiedOrder& order) override;

    ApiResponse<QJsonObject> modify_order(const BrokerCredentials& creds,
                                          const QString& order_id,
                                          const QJsonObject& modifications) override;

    ApiResponse<QJsonObject> cancel_order(const BrokerCredentials& creds,
                                          const QString& order_id) override;

    ApiResponse<QVector<BrokerOrderInfo>> get_orders(const BrokerCredentials& creds) override;

    ApiResponse<QJsonObject> get_trade_book(const BrokerCredentials& creds) override;

    ApiResponse<QVector<BrokerPosition>> get_positions(const BrokerCredentials& creds) override;

    ApiResponse<QVector<BrokerHolding>> get_holdings(const BrokerCredentials& creds) override;

    ApiResponse<BrokerFunds> get_funds(const BrokerCredentials& creds) override;

    ApiResponse<QVector<BrokerQuote>> get_quotes(const BrokerCredentials& creds,
                                                  const QVector<QString>& symbols) override;

    ApiResponse<QVector<BrokerCandle>> get_history(const BrokerCredentials& creds,
                                                    const QString& symbol,
                                                    const QString& resolution,
                                                    const QString& from_date,
                                                    const QString& to_date) override;

protected:
    QMap<QString, QString> auth_headers(const BrokerCredentials& creds) const override;

private:
    // TODO: CTP API实例
    // void* m_trader_api = nullptr;
    // void* m_market_data_api = nullptr;

    bool m_initialized = false;
};

} // namespace fincept::trading
