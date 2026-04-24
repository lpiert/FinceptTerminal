#pragma once
#include "trading/BrokerInterface.h"
#include <QString>

namespace fincept::trading {

/// XTP Broker Implementation - STUB
///
/// TODO: 对接中泰证券XTP API
///
/// XTP (XinTuo Platform) 是中泰证券开发的机构级交易平台
/// 支持A股、基金、债券、期权等品种
/// 被多家券商采用作为量化交易接口
///
/// 官方文档: https://xtp.zts.com.cn/
///
/// 接入要求:
/// 1. 需要在中泰证券或合作券商开户
/// 2. 通常需要100万以上资产
/// 3. 需要签署程序化交易协议
/// 4. 需要通过仿真测试
///
/// 当前实现: 桩代码，返回"Not Implemented"
class XtpBroker : public IBroker {
public:
    XtpBroker();
    ~XtpBroker() override = default;

    // IBroker interface
    BrokerId id() const override { return "xtp"; }
    const char* name() const override { return "XTP (A-Share Institutional)"; }
    const char* base_url() const override { return ""; }  // XTP使用直连IP

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
    // TODO: XTP API实例
    // XTP::API::TraderApi* m_trader_api = nullptr;
    // XTP::API::QuoteApi* m_quote_api = nullptr;

    bool m_initialized = false;
};

} // namespace fincept::trading
