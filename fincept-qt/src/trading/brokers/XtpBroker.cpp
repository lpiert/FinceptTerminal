#include "trading/brokers/XtpBroker.h"
#include "core/logging/Logger.h"

namespace fincept::trading {

XtpBroker::XtpBroker() {
    LOG_INFO("XTP", "XtpBroker created (STUB - not connected)");
    // TODO: 初始化XTP API
    // m_trader_api = XTP::API::TraderApi::CreateTraderApi(1, LOG_LEVEL);
    // m_quote_api = XTP::API::QuoteApi::CreateQuoteApi(1, LOG_LEVEL);
}

BrokerProfile XtpBroker::profile() const {
    BrokerProfile profile;
    profile.id = "xtp";
    profile.display_name = "XTP股票交易";
    profile.region = "CN";
    profile.currency = "CNY";

    // XTP需要的认证字段
    profile.credential_fields = {
        {CredentialField::UserId, "XTP账号", "请输入XTP资金账号", false},
        {CredentialField::Password, "密码", "请输入交易密码", true},
        {CredentialField::ApiKey, "Client ID", "XTP分配的Client ID", false},
        {CredentialField::ApiSecret, "License Key", "XTP授权Key", true},
    };

    // A股交易所
    profile.exchanges = {
        "SSE",  // 上海证券交易所
        "SZSE", // 深圳证券交易所
        "BSE",  // 北京证券交易所
    };

    // A股产品类型
    profile.product_types = {
        {"限价委托", ProductType::Limit},
        {"市价委托", ProductType::Market},
        {"最优五档", ProductType::BestFive},
        {"即时成交剩余撤销", ProductType::FillOrKill},
    };

    profile.supports_intraday = false;  // A股T+1
    profile.supports_bracket_order = false;
    profile.supports_cover_order = false;

    profile.has_native_paper = false;
    profile.default_paper_balance = 1000000.0;

    profile.brokerage_info = "按券商标准，通常万分之2.5起，最低5元";

    return profile;
}

TokenExchangeResponse XtpBroker::exchange_token(const QString& api_key,
                                                 const QString& api_secret,
                                                 const QString& auth_code) {
    Q_UNUSED(api_key);
    Q_UNUSED(api_secret);
    Q_UNUSED(auth_code);

    // TODO: XTP登录流程
    // 1. 设置回调接口
    // 2. 调用Login
    // 3. 等待OnLogin响应

    LOG_WARN("XTP", "exchange_token not implemented (STUB)");
    return {false, "", "XTP login not implemented yet"};
}

OrderPlaceResponse XtpBroker::place_order(const BrokerCredentials& creds,
                                           const UnifiedOrder& order) {
    Q_UNUSED(creds);
    Q_UNUSED(order);

    // TODO: XTP下单
    // XTPTradeParam param;
    // param.market = map_exchange(order.exchange);
    // param.ticker = order.symbol.toStdString().c_str();
    // param.price = order.price;
    // param.quantity = order.quantity;
    // param.side = (order.side == OrderSide::Buy) ? XTP_SIDE_BUY : XTP_SIDE_SELL;
    // param.order_type = map_order_type(order.type);
    // ...
    // uint64_t order_id = m_trader_api->InsertOrder(param);

    LOG_WARN("XTP", "place_order not implemented (STUB)");
    return {false, "", "XTP order placement not implemented yet"};
}

ApiResponse<QJsonObject> XtpBroker::modify_order(const BrokerCredentials& creds,
                                                  const QString& order_id,
                                                  const QJsonObject& modifications) {
    Q_UNUSED(creds);
    Q_UNUSED(order_id);
    Q_UNUSED(modifications);

    // TODO: XTP改单（实际是撤单后重新下单）
    return {false, std::nullopt, "XTP order modification not implemented"};
}

ApiResponse<QJsonObject> XtpBroker::cancel_order(const BrokerCredentials& creds,
                                                  const QString& order_id) {
    Q_UNUSED(creds);
    Q_UNUSED(order_id);

    // TODO: XTP撤单
    // m_trader_api->CancelOrder(order_id.toULongLong());

    return {false, std::nullopt, "XTP order cancellation not implemented"};
}

ApiResponse<QVector<BrokerOrderInfo>> XtpBroker::get_orders(const BrokerCredentials& creds) {
    Q_UNUSED(creds);

    // TODO: 查询报单
    return {false, std::nullopt, "XTP order query not implemented"};
}

ApiResponse<QJsonObject> XtpBroker::get_trade_book(const BrokerCredentials& creds) {
    Q_UNUSED(creds);

    // TODO: 查询成交
    return {false, std::nullopt, "XTP trade book not implemented"};
}

ApiResponse<QVector<BrokerPosition>> XtpBroker::get_positions(const BrokerCredentials& creds) {
    Q_UNUSED(creds);

    // TODO: 查询持仓
    return {false, std::nullopt, "XTP position query not implemented"};
}

ApiResponse<QVector<BrokerHolding>> XtpBroker::get_holdings(const BrokerCredentials& creds) {
    Q_UNUSED(creds);

    // TODO: XTP查询持仓（股票叫holdings）
    return {false, std::nullopt, "XTP holdings query not implemented"};
}

ApiResponse<BrokerFunds> XtpBroker::get_funds(const BrokerCredentials& creds) {
    Q_UNUSED(creds);

    // TODO: 查询资金
    return {false, std::nullopt, "XTP funds query not implemented"};
}

ApiResponse<QVector<BrokerQuote>> XtpBroker::get_quotes(const BrokerCredentials& creds,
                                                         const QVector<QString>& symbols) {
    Q_UNUSED(creds);
    Q_UNUSED(symbols);

    // TODO: XTP行情通过Quote API获取
    // m_quote_api->SubscribeMarketData(symbols);

    return {false, std::nullopt, "XTP quotes not implemented (use MarketDataService instead)"};
}

ApiResponse<QVector<BrokerCandle>> XtpBroker::get_history(const BrokerCredentials& creds,
                                                           const QString& symbol,
                                                           const QString& resolution,
                                                           const QString& from_date,
                                                           const QString& to_date) {
    Q_UNUSED(creds);
    Q_UNUSED(symbol);
    Q_UNUSED(resolution);
    Q_UNUSED(from_date);
    Q_UNUSED(to_date);

    // XTP不提供历史数据，需要使用其他数据源
    return {false, std::nullopt, "XTP does not provide historical data"};
}

QMap<QString, QString> XtpBroker::auth_headers(const BrokerCredentials& creds) const {
    Q_UNUSED(creds);
    // XTP不使用HTTP，不需要headers
    return {};
}

} // namespace fincept::trading
