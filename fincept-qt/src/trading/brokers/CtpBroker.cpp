#include "trading/brokers/CtpBroker.h"
#include "core/logging/Logger.h"

namespace fincept::trading {

CtpBroker::CtpBroker() {
    LOG_INFO("CTP", "CtpBroker created (STUB - not connected)");
    // TODO: 初始化CTP API
    // m_trader_api = CThostFtdcTraderApi::CreateFtdcTraderApi(flow_path);
    // m_market_data_api = CThostFtdcMdApi::CreateFtdcMdApi(flow_path);
}

BrokerProfile CtpBroker::profile() const {
    BrokerProfile profile;
    profile.id = "ctp";
    profile.display_name = "CTP期货";
    profile.region = "CN";
    profile.currency = "CNY";

    // CTP需要的认证字段
    profile.credential_fields = {
        {CredentialField::UserId, "投资者账号", "请输入投资者代码", false},
        {CredentialField::Password, "密码", "请输入交易密码", true},
        {CredentialField::ApiKey, "经纪商代码", "例如: 9999", false},
        {CredentialField::ApiSecret, "授权码", "可选", true},
    };

    // 期货交易所
    profile.exchanges = {
        "SHF",  // 上海期货交易所
        "DCE",  // 大连商品交易所
        "CZC",  // 郑州商品交易所
        "CFX",  // 中国金融期货交易所
        "INE",  // 上海国际能源交易中心
    };

    // 期货产品类型
    profile.product_types = {
        {"开仓", ProductType::Open},
        {"平仓", ProductType::Close},
        {"平今", ProductType::CloseToday},
        {"平昨", ProductType::CloseYesterday},
    };

    profile.supports_intraday = true;
    profile.supports_bracket_order = false;  // CTP原生不支持，需自行实现
    profile.supports_cover_order = false;

    profile.has_native_paper = false;
    profile.default_paper_balance = 1000000.0;

    profile.brokerage_info = "按期货公司标准，通常万分之0.5~1起";

    return profile;
}

TokenExchangeResponse CtpBroker::exchange_token(const QString& api_key,
                                                 const QString& api_secret,
                                                 const QString& auth_code) {
    Q_UNUSED(api_key);
    Q_UNUSED(api_secret);
    Q_UNUSED(auth_code);

    // TODO: CTP登录流程
    // 1. 注册SPI回调
    // 2. 连接前置机
    // 3. 调用ReqUserLogin
    // 4. 等待OnRspUserLogin回调

    LOG_WARN("CTP", "exchange_token not implemented (STUB)");
    return {false, "", "CTP login not implemented yet"};
}

OrderPlaceResponse CtpBroker::place_order(const BrokerCredentials& creds,
                                           const UnifiedOrder& order) {
    Q_UNUSED(creds);
    Q_UNUSED(order);

    // TODO: CTP下单
    // CThostFtdcInputOrderField req;
    // memset(&req, 0, sizeof(req));
    // strcpy(req.BrokerID, creds.api_key.toStdString().c_str());
    // strcpy(req.InvestorID, creds.user_id.toStdString().c_str());
    // strcpy(req.InstrumentID, order.symbol.toStdString().c_str());
    // req.Direction = (order.side == OrderSide::Buy) ? THOST_FTDC_D_Buy : THOST_FTDC_D_Sell;
    // req.CombOffsetFlag[0] = map_product_type(order.product);
    // req.VolumeTotalOriginal = order.quantity;
    // req.LimitPrice = order.price;
    // ...
    // m_trader_api->ReqOrderInsert(&req, request_id++);

    LOG_WARN("CTP", "place_order not implemented (STUB)");
    return {false, "", "CTP order placement not implemented yet"};
}

ApiResponse<QJsonObject> CtpBroker::modify_order(const BrokerCredentials& creds,
                                                  const QString& order_id,
                                                  const QJsonObject& modifications) {
    Q_UNUSED(creds);
    Q_UNUSED(order_id);
    Q_UNUSED(modifications);

    // TODO: CTP改单（实际是撤单后重新下单）
    return {false, std::nullopt, "CTP order modification not implemented"};
}

ApiResponse<QJsonObject> CtpBroker::cancel_order(const BrokerCredentials& creds,
                                                  const QString& order_id) {
    Q_UNUSED(creds);
    Q_UNUSED(order_id);

    // TODO: CTP撤单
    // CThostFtdcInputOrderActionField action;
    // ...
    // m_trader_api->ReqOrderAction(&action, request_id++);

    return {false, std::nullopt, "CTP order cancellation not implemented"};
}

ApiResponse<QVector<BrokerOrderInfo>> CtpBroker::get_orders(const BrokerCredentials& creds) {
    Q_UNUSED(creds);

    // TODO: 查询报单
    // m_trader_api->ReqQryOrder(&qry, request_id++);

    return {false, std::nullopt, "CTP order query not implemented"};
}

ApiResponse<QJsonObject> CtpBroker::get_trade_book(const BrokerCredentials& creds) {
    Q_UNUSED(creds);

    // TODO: 查询成交
    return {false, std::nullopt, "CTP trade book not implemented"};
}

ApiResponse<QVector<BrokerPosition>> CtpBroker::get_positions(const BrokerCredentials& creds) {
    Q_UNUSED(creds);

    // TODO: 查询持仓
    // m_trader_api->ReqQryInvestorPosition(&qry, request_id++);

    return {false, std::nullopt, "CTP position query not implemented"};
}

ApiResponse<QVector<BrokerHolding>> CtpBroker::get_holdings(const BrokerCredentials& creds) {
    Q_UNUSED(creds);

    // 期货没有holdings概念，只有positions
    return {true, QVector<BrokerHolding>{}, ""};
}

ApiResponse<BrokerFunds> CtpBroker::get_funds(const BrokerCredentials& creds) {
    Q_UNUSED(creds);

    // TODO: 查询资金
    // m_trader_api->ReqQryTradingAccount(&qry, request_id++);

    return {false, std::nullopt, "CTP funds query not implemented"};
}

ApiResponse<QVector<BrokerQuote>> CtpBroker::get_quotes(const BrokerCredentials& creds,
                                                         const QVector<QString>& symbols) {
    Q_UNUSED(creds);
    Q_UNUSED(symbols);

    // TODO: CTP行情通过MarketData API获取
    // 需要订阅行情: m_market_data_api->SubscribeMarketData(instruments, count);

    return {false, std::nullopt, "CTP quotes not implemented (use MarketDataService instead)"};
}

ApiResponse<QVector<BrokerCandle>> CtpBroker::get_history(const BrokerCredentials& creds,
                                                           const QString& symbol,
                                                           const QString& resolution,
                                                           const QString& from_date,
                                                           const QString& to_date) {
    Q_UNUSED(creds);
    Q_UNUSED(symbol);
    Q_UNUSED(resolution);
    Q_UNUSED(from_date);
    Q_UNUSED(to_date);

    // CTP不提供历史数据，需要使用其他数据源
    return {false, std::nullopt, "CTP does not provide historical data"};
}

QMap<QString, QString> CtpBroker::auth_headers(const BrokerCredentials& creds) const {
    Q_UNUSED(creds);
    // CTP不使用HTTP，不需要headers
    return {};
}

} // namespace fincept::trading
