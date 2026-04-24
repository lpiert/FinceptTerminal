#pragma once
#include "core/result/Result.h"
#include <QObject>
#include <QString>
#include <QVector>
#include <QMap>
#include <QJsonObject>

namespace fincept::services {

/// Level 2 Order Book Entry (买/卖盘档位)
struct Level2Order {
    double price = 0.0;
    qint64 volume = 0;      // 手数
    int orders = 0;          // 委托笔数（部分交易所提供）
};

/// Level 2 Tick Data (逐笔成交)
struct Level2Tick {
    qint64 timestamp = 0;    // 毫秒级时间戳
    double price = 0.0;
    qint64 volume = 0;
    QString direction;       // "B"=Buy, "S"=Sell, "N"=Neutral
};

/// Level 2 Market Depth (十档行情 + 逐笔)
struct Level2Depth {
    QString symbol;
    qint64 timestamp = 0;

    QVector<Level2Order> bids;  // 买盘（通常10档或50档）
    QVector<Level2Order> asks;  // 卖盘

    QVector<Level2Tick> ticks;  // 逐笔成交（可选，数据量大）

    // 加权均价
    double bid_weighted_avg = 0.0;
    double ask_weighted_avg = 0.0;

    // 买卖队列总委托量
    qint64 total_bid_volume = 0;
    qint64 total_ask_volume = 0;
};

/// Level 2 Data Service - STUB
///
/// TODO: 对接付费数据源
/// - 上交所Level 2: 需通过上证所信息网络有限公司授权
/// - 深交所Level 2: 需通过深圳证券信息有限公司授权
/// - 推荐供应商:
///   1. Wind资讯 (万得) - 机构级，昂贵
///   2. EastMoney (东方财富Choice) - 中等价位
///   3. JoinQuant (聚宽) / RiceQuant (米筐) - 量化平台，提供API
///   4. Tushare Pro - 个人可用，积分制
///
/// 当前实现: 返回空数据或模拟数据，用于UI开发和测试
class Level2DataService : public QObject {
    Q_OBJECT
public:
    static Level2DataService& instance();

    /// 获取Level 2十档行情
    ///
    /// TODO: 替换为真实API调用
    /// @param symbol Symbol格式: "600519.SS", "000001.SZ"
    /// @return Level2Depth 包含买卖十档和逐笔数据
    Result<Level2Depth> get_depth(const QString& symbol);

    /// 订阅Level 2实时推送（WebSocket）
    ///
    /// TODO: 实现WebSocket连接
    /// @param symbol 订阅的symbol
    /// @param callback 每次收到推送时调用
    void subscribe_depth(const QString& symbol,
                         std::function<void(const Level2Depth&)> callback);

    /// 取消订阅
    void unsubscribe_depth(const QString& symbol);

    /// 获取历史逐笔成交（付费接口）
    ///
    /// TODO: 对接历史数据API
    /// @param symbol Symbol
    /// @param date 日期 YYYY-MM-DD
    /// @param limit 最大返回条数（默认1000）
    Result<QVector<Level2Tick>> get_historical_ticks(const QString& symbol,
                                                      const QString& date,
                                                      int limit = 1000);

    /// 检查Level 2权限
    /// @return true if authorized
    bool is_authorized() const { return m_authorized; }

    /// 设置API密钥（后续对接时调用）
    void set_api_key(const QString& key) { m_api_key = key; }

signals:
    /// Level 2数据更新信号
    void depth_updated(const QString& symbol, const Level2Depth& depth);

private:
    Level2DataService();

    /// 生成模拟Level 2数据（用于开发测试）
    Level2Depth generate_mock_depth(const QString& symbol, double current_price);

    bool m_authorized = false;
    QString m_api_key;

    // 订阅管理
    QMap<QString, std::function<void(const Level2Depth&)>> m_subscriptions;
};

} // namespace fincept::services
