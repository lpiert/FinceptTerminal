#pragma once
#include "core/result/Result.h"
#include <QString>
#include <QDateTime>
#include <QMap>

namespace fincept::trading {

struct UnifiedOrder;
struct QuoteData;

/// China Trading Rules Engine
///
/// 实现中国A股/期货的特殊交易规则检查
/// 所有检查在下单前执行，防止违规订单发送到交易所
///
/// 当前可立即开发，无需实盘API
class ChinaTradingRules {
public:
    static ChinaTradingRules& instance();

    /// 验证订单是否符合A股规则
    ///
    /// 检查项:
    /// 1. T+1规则（当日买入不可卖出）
    /// 2. 涨跌停板限制（±10% / ±20% / ±5%）
    /// 3. 最小交易单位（100股整数倍）
    /// 4. ST股票特殊规则
    /// 5. 科创板/创业板权限
    Result<void> validate_a_share_order(const UnifiedOrder& order,
                                         const QuoteData& current_quote);

    /// 验证期货订单
    ///
    /// 检查项:
    /// 1. 最小变动价位
    /// 2. 合约乘数
    /// 3. 保证金比例
    /// 4. 持仓限额
    Result<void> validate_futures_order(const UnifiedOrder& order,
                                         const QuoteData& current_quote);

    /// 检查T+1规则
    ///
    /// TODO: 查询今日买入记录
    /// @param symbol 股票代码
    /// @param quantity 拟卖出数量
    /// @return true if can sell
    bool can_sell_today(const QString& symbol, int quantity);

    /// 计算涨跌停价格
    ///
    /// @param symbol 股票代码
    /// @param prev_close 昨日收盘价
    /// @return pair<limit_up, limit_down>
    QPair<double, double> calculate_price_limits(const QString& symbol, double prev_close);

    /// 检查是否为ST股票
    bool is_st_stock(const QString& symbol);

    /// 检查是否为科创板股票 (688xxx)
    bool is_star_market(const QString& symbol);

    /// 检查是否为创业板股票 (300xxx, 301xxx)
    bool is_chi_next(const QString& symbol);

    /// 获取最小交易单位
    ///
    /// A股: 100股
    /// 科创板: 200股起，之后1股递增
    /// 港股: 每手数量不同（需查询）
    int get_min_trade_unit(const QString& symbol);

    /// 记录今日买入（用于T+1检查）
    void record_today_buy(const QString& symbol, int quantity);

    /// 清除今日交易记录（每日收盘后调用）
    void clear_daily_records();

private:
    ChinaTradingRules() = default;

    // 今日买入记录: symbol -> total_quantity_bought_today
    QMap<QString, int> m_today_buys;

    // ST股票列表（缓存）
    QSet<QString> m_st_stocks;

    // 科创板权限标志
    bool m_star_market_enabled = false;

    // 创业板权限标志
    bool m_chi_next_enabled = false;
};

} // namespace fincept::trading
