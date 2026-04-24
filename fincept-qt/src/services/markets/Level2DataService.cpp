#include "services/markets/Level2DataService.h"
#include "core/logging/Logger.h"
#include <QDateTime>
#include <random>

namespace fincept::services {

Level2DataService& Level2DataService::instance() {
    static Level2DataService s;
    return s;
}

Level2DataService::Level2DataService() {
    LOG_INFO("Level2Data", "Level2DataService initialized (STUB - not authorized)");
}

Result<Level2Depth> Level2DataService::get_depth(const QString& symbol) {
    // TODO: 替换为真实API调用
    // 示例伪代码:
    // auto response = http_client.get("/api/level2/depth", {{"symbol", symbol}});
    // if (response.ok()) {
    //     return parse_depth(response.json());
    // } else {
    //     return Err("Failed to fetch Level 2 data: " + response.error());
    // }

    if (!m_authorized) {
        LOG_WARN("Level2Data",
                 QString("Level 2 not authorized - returning mock data for %1").arg(symbol));
        // 返回模拟数据用于UI开发
        double mock_price = 100.0;  // TODO: 从Level 1行情获取当前价
        return Ok(generate_mock_depth(symbol, mock_price));
    }

    return Err("Level 2 service not implemented yet");
}

void Level2DataService::subscribe_depth(const QString& symbol,
                                         std::function<void(const Level2Depth&)> callback) {
    // TODO: 实现WebSocket订阅
    // 示例伪代码:
    // websocket_client.subscribe("level2:" + symbol, [callback](json data) {
    //     auto depth = parse_depth(data);
    //     callback(depth);
    // });

    m_subscriptions[symbol] = callback;
    LOG_WARN("Level2Data",
             QString("Level 2 subscription stubbed for %1 (no real-time data)").arg(symbol));
}

void Level2DataService::unsubscribe_depth(const QString& symbol) {
    m_subscriptions.remove(symbol);
}

Result<QVector<Level2Tick>> Level2DataService::get_historical_ticks(const QString& symbol,
                                                                     const QString& date,
                                                                     int limit) {
    // TODO: 对接历史逐笔数据API
    // 注意: 历史tick数据量巨大，通常需要付费且需要特殊权限

    Q_UNUSED(symbol);
    Q_UNUSED(date);
    Q_UNUSED(limit);

    return Err("Historical tick data not available (requires paid API)");
}

Level2Depth Level2DataService::generate_mock_depth(const QString& symbol, double current_price) {
    // 生成模拟的十档行情（仅用于UI开发和测试）
    Level2Depth depth;
    depth.symbol = symbol;
    depth.timestamp = QDateTime::currentMSecsSinceEpoch();

    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> price_dist(0.01, 0.05);  // 价格波动1-5%
    std::uniform_int_distribution<> volume_dist(10, 1000);     // 成交量10-1000手

    // 生成买盘10档
    for (int i = 0; i < 10; ++i) {
        Level2Order order;
        order.price = current_price * (1.0 - price_dist(gen) * (i + 1) * 0.1);
        order.volume = volume_dist(gen);
        order.orders = std::max(1, static_cast<int>(order.volume / 10));
        depth.bids.append(order);
        depth.total_bid_volume += order.volume;
    }

    // 生成卖盘10档
    for (int i = 0; i < 10; ++i) {
        Level2Order order;
        order.price = current_price * (1.0 + price_dist(gen) * (i + 1) * 0.1);
        order.volume = volume_dist(gen);
        order.orders = std::max(1, static_cast<int>(order.volume / 10));
        depth.asks.append(order);
        depth.total_ask_volume += order.volume;
    }

    // 计算加权均价
    if (depth.total_bid_volume > 0) {
        double bid_sum = 0;
        for (const auto& bid : depth.bids) {
            bid_sum += bid.price * bid.volume;
        }
        depth.bid_weighted_avg = bid_sum / depth.total_bid_volume;
    }

    if (depth.total_ask_volume > 0) {
        double ask_sum = 0;
        for (const auto& ask : depth.asks) {
            ask_sum += ask.price * ask.volume;
        }
        depth.ask_weighted_avg = ask_sum / depth.total_ask_volume;
    }

    return depth;
}

} // namespace fincept::services
