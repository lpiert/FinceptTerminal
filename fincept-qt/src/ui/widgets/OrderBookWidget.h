#pragma once
#include "services/markets/Level2DataService.h"
#include <QWidget>
#include <QVector>
#include <QLabel>

namespace fincept::ui {

/// Level 2 Order Book Widget - 十档行情显示
///
/// 显示买卖十档行情、加权均价、买卖队列总量
/// 基于 Level2DataService（当前为桩代码，返回模拟数据）
///
/// UI团队可以立即使用此组件开发，后续接入真实API无需修改UI代码
class OrderBookWidget : public QWidget {
    Q_OBJECT
public:
    explicit OrderBookWidget(QWidget* parent = nullptr);
    ~OrderBookWidget() override = default;

    /// 设置要监听的symbol
    void set_symbol(const QString& symbol);

    /// 获取当前symbol
    QString symbol() const { return m_symbol; }

    /// 刷新数据（手动触发）
    void refresh();

protected:
    void paintEvent(QPaintEvent* event) override;

private slots:
    /// DataHub推送的Level 2数据更新
    void on_depth_updated(const QString& symbol, const services::Level2Depth& depth);

private:
    /// 初始化UI布局
    void setup_ui();

    /// 渲染买盘
    void render_bids(const QVector<services::Level2Order>& bids);

    /// 渲染卖盘
    void render_asks(const QVector<services::Level2Order>& asks);

    /// 更新统计信息（加权均价、总量）
    void update_statistics(const services::Level2Depth& depth);

    // UI元素
    QLabel* m_symbol_label = nullptr;
    QLabel* m_bid_avg_label = nullptr;   // 买盘加权均价
    QLabel* m_ask_avg_label = nullptr;   // 卖盘加权均价
    QLabel* m_bid_total_label = nullptr; // 买盘总量
    QLabel* m_ask_total_label = nullptr; // 卖盘总量

    // 十档行情表格
    QVector<QLabel*> m_bid_price_labels;
    QVector<QLabel*> m_bid_volume_labels;
    QVector<QLabel*> m_ask_price_labels;
    QVector<QLabel*> m_ask_volume_labels;

    // 数据
    QString m_symbol;
    services::Level2Depth m_current_depth;

    // 定时器（用于模拟实时刷新）
    QTimer* m_refresh_timer = nullptr;
};

} // namespace fincept::ui
