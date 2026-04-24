#include "trading/ChinaTradingRules.h"
#include "trading/TradingTypes.h"
#include "core/logging/Logger.h"

namespace fincept::trading {

ChinaTradingRules& ChinaTradingRules::instance() {
    static ChinaTradingRules s;
    return s;
}

Result<void> ChinaTradingRules::validate_a_share_order(const UnifiedOrder& order,
                                                        const QuoteData& current_quote) {
    // 1. T+1检查
    if (order.side == OrderSide::Sell) {
        if (!can_sell_today(order.symbol, static_cast<int>(order.quantity))) {
            return Err("T+1规则: 今日买入的股票不可当日卖出");
        }
    }

    // 2. 最小交易单位检查
    int min_unit = get_min_trade_unit(order.symbol);
    if (static_cast<int>(order.quantity) % min_unit != 0) {
        return Err(QString("交易数量必须是%1的整数倍").arg(min_unit));
    }

    // 3. 涨跌停板检查
    auto [limit_up, limit_down] = calculate_price_limits(order.symbol, current_quote.previous_close);

    if (order.type == OrderType::Limit) {
        if (order.price > limit_up) {
            return Err(QString("价格超过涨停价: %1").arg(limit_up, 0, 'f', 2));
        }
        if (order.price < limit_down) {
            return Err(QString("价格低于跌停价: %1").arg(limit_down, 0, 'f', 2));
        }
    }

    // 4. 科创板/创业板权限检查
    if (is_star_market(order.symbol) && !m_star_market_enabled) {
        return Err("科创板交易权限未开通");
    }

    if (is_chi_next(order.symbol) && !m_chi_next_enabled) {
        return Err("创业板交易权限未开通");
    }

    // 5. ST股票特殊检查（涨跌幅±5%）
    if (is_st_stock(order.symbol)) {
        double st_limit_up = current_quote.previous_close * 1.05;
        double st_limit_down = current_quote.previous_close * 0.95;

        if (order.type == OrderType::Limit) {
            if (order.price > st_limit_up || order.price < st_limit_down) {
                return Err("ST股票涨跌幅限制为±5%");
            }
        }
    }

    return Ok();
}

Result<void> ChinaTradingRules::validate_futures_order(const UnifiedOrder& order,
                                                        const QuoteData& /*current_quote*/) {
    Q_UNUSED(order);

    // TODO: 实现期货规则检查
    // 1. 最小变动价位
    // 2. 保证金比例
    // 3. 持仓限额
    // 4. 大户报告制度

    return Ok();
}

bool ChinaTradingRules::can_sell_today(const QString& symbol, int quantity) {
    // TODO: 查询今日买入记录
    // 当前简化实现：假设可以卖出

    int bought_today = m_today_buys.value(symbol, 0);
    if (quantity > bought_today) {
        // 卖出的数量超过了今日买入的数量，可能是昨日持仓，允许卖出
        return true;
    }

    // 如果全部是今日买入，则不允许卖出
    LOG_WARN("TradingRules", QString("T+1 rule blocked: trying to sell %1 shares of %2 bought today")
                                 .arg(quantity).arg(symbol));
    return false;
}

QPair<double, double> ChinaTradingRules::calculate_price_limits(const QString& symbol,
                                                                 double prev_close) {
    double limit_ratio = 0.10;  // 默认±10%

    // ST股票: ±5%
    if (is_st_stock(symbol)) {
        limit_ratio = 0.05;
    }
    // 科创板: ±20%
    else if (is_star_market(symbol)) {
        limit_ratio = 0.20;
    }
    // 创业板: ±20%
    else if (is_chi_next(symbol)) {
        limit_ratio = 0.20;
    }

    double limit_up = prev_close * (1.0 + limit_ratio);
    double limit_down = prev_close * (1.0 - limit_ratio);

    return qMakePair(limit_up, limit_down);
}

bool ChinaTradingRules::is_st_stock(const QString& symbol) {
    // ST股票标识: 名称包含"ST"或"*ST"
    // TODO: 从数据源获取ST股票列表
    return symbol.contains("ST", Qt::CaseInsensitive);
}

bool ChinaTradingRules::is_star_market(const QString& symbol) {
    // 科创板: 688xxx
    return symbol.startsWith("688");
}

bool ChinaTradingRules::is_chi_next(const QString& symbol) {
    // 创业板: 300xxx, 301xxx
    return symbol.startsWith("300") || symbol.startsWith("301");
}

int ChinaTradingRules::get_min_trade_unit(const QString& symbol) {
    // 科创板: 200股起，之后1股递增
    if (is_star_market(symbol)) {
        return 1;  // 超过200股后可以1股递增
    }

    // A股主板: 100股整数倍
    return 100;
}

void ChinaTradingRules::record_today_buy(const QString& symbol, int quantity) {
    m_today_buys[symbol] += quantity;
    LOG_INFO("TradingRules",
             QString("Recorded buy: %1 shares of %2 (total today: %3)")
                 .arg(quantity).arg(symbol).arg(m_today_buys[symbol]));
}

void ChinaTradingRules::clear_daily_records() {
    m_today_buys.clear();
    LOG_INFO("TradingRules", "Daily trading records cleared");
}

} // namespace fincept::trading
