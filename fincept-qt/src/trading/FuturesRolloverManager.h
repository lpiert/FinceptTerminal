#pragma once
#include <QString>
#include <QVector>
#include <QMap>
#include <QDateTime>

namespace fincept::trading {

/// Futures Contract Rollover Manager
///
/// 管理期货合约的自动换月逻辑
///
/// 期货合约有到期日，需要在到期前切换到下一个主力合约。
/// 例如: rb2405 (2024年5月到期) → rb2410 (2024年10月到期)
///
/// TODO: 实现以下功能
/// 1. 查询合约到期日
/// 2. 根据成交量/持仓量判断主力合约
/// 3. 自动切换推荐的主力合约
/// 4. 支持手动指定合约
class FuturesRolloverManager {
public:
    static FuturesRolloverManager& instance();

    /// 获取当前主力合约
    ///
    /// TODO: 从交易所API或数据源获取真实的主力合约信息
    /// @param base_symbol 品种代码，如 "rb" (螺纹钢), "IF" (沪深300期指)
    /// @param exchange 交易所代码，如 "SHF", "CFX"
    /// @return 主力合约symbol，如 "rb2405.SHF"
    QString get_main_contract(const QString& base_symbol, const QString& exchange);

    /// 获取下一个合约月份
    ///
    /// @param current_contract 当前合约，如 "rb2405"
    /// @return 下一个合约，如 "rb2410"
    QString get_next_contract(const QString& current_contract);

    /// 检查是否需要换月
    ///
    /// @param current_contract 当前合约
    /// @param days_before_expiry 到期前多少天开始提示换月（默认20天）
    /// @return true if should roll over
    bool should_rollover(const QString& current_contract, int days_before_expiry = 20);

    /// 获取合约到期日
    ///
    /// TODO: 从交易所获取真实到期日
    /// @param contract 合约代码，如 "rb2405.SHF"
    /// @return 到期日期
    QDateTime get_expiry_date(const QString& contract);

    /// 注册合约换月回调
    ///
    /// 当检测到需要换月时，调用此回调通知UI更新
    using RolloverCallback = std::function<void(const QString& old_contract,
                                                 const QString& new_contract)>;
    void register_callback(const QString& base_symbol, RolloverCallback callback);

    /// 检查所有注册的合约是否需要换月
    void check_all_contracts();

private:
    FuturesRolloverManager() = default;

    /// 生成模拟的到期日（用于开发测试）
    QDateTime generate_mock_expiry(const QString& contract);

    // 换月回调映射: base_symbol -> callback
    QMap<QString, RolloverCallback> m_callbacks;

    // 缓存的主力合约: "base_symbol:exchange" -> main_contract
    QMap<QString, QString> m_main_contracts;
};

} // namespace fincept::trading
