#include "trading/FuturesRolloverManager.h"
#include "core/logging/Logger.h"
#include <QTimer>

namespace fincept::trading {

FuturesRolloverManager& FuturesRolloverManager::instance() {
    static FuturesRolloverManager s;
    return s;
}

QString FuturesRolloverManager::get_main_contract(const QString& base_symbol,
                                                    const QString& exchange) {
    // TODO: 从交易所API或数据源获取真实的主力合约
    // 当前实现: 返回模拟的主力合约

    QString key = base_symbol + ":" + exchange;

    // 如果已有缓存，直接返回
    if (m_main_contracts.contains(key)) {
        return m_main_contracts[key];
    }

    // TODO: 根据成交量/持仓量判断主力合约
    // 示例伪代码:
    // auto contracts = get_all_contracts(base_symbol, exchange);
    // for (const auto& contract : contracts) {
    //     auto volume = get_volume(contract);
    //     if (volume > max_volume) {
    //         max_volume = volume;
    //         main_contract = contract;
    //     }
    // }

    // 模拟实现: 假设当前主力合约是2405
    QString mock_main = base_symbol + "2405";
    m_main_contracts[key] = mock_main;

    LOG_INFO("FuturesRollover",
             QString("Main contract for %1 (%2): %3 (MOCK)")
                 .arg(base_symbol)
                 .arg(exchange)
                 .arg(mock_main));

    return mock_main;
}

QString FuturesRolloverManager::get_next_contract(const QString& current_contract) {
    // TODO: 根据合约月份规则计算下一个合约
    // 不同品种的合约月份不同:
    // - 螺纹钢: 1, 5, 9月
    // - 黄金: 2, 4, 6, 8, 10, 12月
    // - 股指期货: 当月、下月、随后两个季月

    // 简单实现: 提取月份，加5个月（针对螺纹钢等1-5-9品种）
    QRegExp rx("(\\d{2})(\\d{2})");
    if (rx.indexIn(current_contract) != -1) {
        int year = rx.cap(1).toInt();
        int month = rx.cap(2).toInt();

        // 切换到下一个合约月份（简化逻辑）
        QVector<int> contract_months;
        if (current_contract.startsWith("rb") || current_contract.startsWith("hc")) {
            // 螺纹钢、热卷: 1, 5, 9月
            contract_months = {1, 5, 9};
        } else if (current_contract.startsWith("IF") || current_contract.startsWith("IC")) {
            // 股指期货: 连续四个月
            contract_months = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12};
        } else {
            // 默认: 1, 5, 9月
            contract_months = {1, 5, 9};
        }

        // 找到当前月份之后的下一个合约月
        for (int m : contract_months) {
            if (m > month) {
                return current_contract.left(current_contract.length() - 4) +
                       QString("%1%2").arg(year, 2, 10, QChar('0')).arg(m, 2, 10, QChar('0'));
            }
        }

        // 跨年
        return current_contract.left(current_contract.length() - 4) +
               QString("%1%2").arg(year + 1, 2, 10, QChar('0')).arg(contract_months.first(), 2, 10, QChar('0'));
    }

    return current_contract;
}

bool FuturesRolloverManager::should_rollover(const QString& current_contract,
                                              int days_before_expiry) {
    // TODO: 检查是否接近到期日
    QDateTime expiry = get_expiry_date(current_contract);
    QDateTime now = QDateTime::currentDateTime();

    if (!expiry.isValid()) {
        LOG_WARN("FuturesRollover",
                 QString("Invalid expiry date for %1").arg(current_contract));
        return false;
    }

    int days_to_expiry = now.daysTo(expiry);
    if (days_to_expiry <= days_before_expiry) {
        LOG_INFO("FuturesRollover",
                 QString("%1 expires in %2 days - should rollover!")
                     .arg(current_contract)
                     .arg(days_to_expiry));
        return true;
    }

    return false;
}

QDateTime FuturesRolloverManager::get_expiry_date(const QString& contract) {
    // TODO: 从交易所获取真实到期日
    // 当前实现: 生成模拟的到期日

    return generate_mock_expiry(contract);
}

void FuturesRolloverManager::register_callback(const QString& base_symbol,
                                                RolloverCallback callback) {
    m_callbacks[base_symbol] = callback;
}

void FuturesRolloverManager::check_all_contracts() {
    // TODO: 定期检查所有合约是否需要换月
    // 可以设置一个定时器，每天检查一次

    for (auto it = m_callbacks.begin(); it != m_callbacks.end(); ++it) {
        const QString& base_symbol = it.key();
        auto& callback = it.value();

        // 获取当前主力合约
        QString main = get_main_contract(base_symbol, "SHF");  // 示例交易所

        // 检查是否需要换月
        if (should_rollover(main)) {
            QString next = get_next_contract(main);
            LOG_INFO("FuturesRollover",
                     QString("Rollover detected: %1 -> %2").arg(main).arg(next));

            // 调用回调通知UI
            callback(main, next);

            // 更新缓存
            m_main_contracts[base_symbol + ":SHF"] = next;
        }
    }
}

QDateTime FuturesRolloverManager::generate_mock_expiry(const QString& contract) {
    // 模拟到期日: 假设合约代码中的月份就是到期月份
    // 例如: rb2405 -> 2024年5月15日（期货通常在该月15日左右到期）

    QRegExp rx("(\\d{2})(\\d{2})");
    if (rx.indexIn(contract) != -1) {
        int year = 2000 + rx.cap(1).toInt();
        int month = rx.cap(2).toInt();

        // 期货通常在合约月份的15日到期（遇节假日顺延）
        return QDateTime(QDate(year, month, 15), QTime(15, 0, 0));
    }

    // 默认返回一年后
    return QDateTime::currentDateTime().addYears(1);
}

} // namespace fincept::trading
