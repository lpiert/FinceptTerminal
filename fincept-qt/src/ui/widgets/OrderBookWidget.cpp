#include "ui/widgets/OrderBookWidget.h"
#include "ui/theme/Theme.h"
#include "core/logging/Logger.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QGridLayout>
#include <QPainter>
#include <QTimer>

namespace fincept::ui {

OrderBookWidget::OrderBookWidget(QWidget* parent)
    : QWidget(parent) {
    setup_ui();

    // 启动定时器，每3秒刷新一次（模拟实时数据）
    m_refresh_timer = new QTimer(this);
    connect(m_refresh_timer, &QTimer::timeout, this, [this]() {
        if (!m_symbol.isEmpty()) {
            refresh();
        }
    });
    m_refresh_timer->start(3000);

    LOG_INFO("OrderBook", "OrderBookWidget created (using mock Level 2 data)");
}

void OrderBookWidget::setup_ui() {
    auto* main_layout = new QVBoxLayout(this);
    main_layout->setSpacing(4);
    main_layout->setContentsMargins(8, 8, 8, 8);

    // 标题栏
    m_symbol_label = new QLabel("Symbol: --", this);
    m_symbol_label->setStyleSheet("font-weight: bold; font-size: 14px; color: #ffffff;");
    main_layout->addWidget(m_symbol_label);

    // 统计信息栏
    auto* stats_layout = new QHBoxLayout();

    auto* bid_stats_layout = new QVBoxLayout();
    bid_stats_layout->addWidget(new QLabel("买盘加权均价:", this));
    m_bid_avg_label = new QLabel("--", this);
    m_bid_avg_label->setStyleSheet("color: #00ff00; font-weight: bold;");
    bid_stats_layout->addWidget(m_bid_avg_label);

    bid_stats_layout->addWidget(new QLabel("买盘总量:", this));
    m_bid_total_label = new QLabel("--", this);
    m_bid_total_label->setStyleSheet("color: #00ff00;");
    bid_stats_layout->addWidget(m_bid_total_label);

    auto* ask_stats_layout = new QVBoxLayout();
    ask_stats_layout->addWidget(new QLabel("卖盘加权均价:", this));
    m_ask_avg_label = new QLabel("--", this);
    m_ask_avg_label->setStyleSheet("color: #ff0000; font-weight: bold;");
    ask_stats_layout->addWidget(m_ask_avg_label);

    ask_stats_layout->addWidget(new QLabel("卖盘总量:", this));
    m_ask_total_label = new QLabel("--", this);
    m_ask_total_label->setStyleSheet("color: #ff0000;");
    ask_stats_layout->addWidget(m_ask_total_label);

    stats_layout->addLayout(bid_stats_layout);
    stats_layout->addStretch();
    stats_layout->addLayout(ask_stats_layout);
    main_layout->addLayout(stats_layout);

    // 十档行情表格
    auto* grid_layout = new QGridLayout();
    grid_layout->setHorizontalSpacing(10);
    grid_layout->setVerticalSpacing(2);

    // 表头
    auto* bid_price_header = new QLabel("买价", this);
    bid_price_header->setStyleSheet("color: #00ff00; font-weight: bold;");
    auto* bid_volume_header = new QLabel("买量", this);
    bid_volume_header->setStyleSheet("color: #00ff00; font-weight: bold;");
    auto* ask_price_header = new QLabel("卖价", this);
    ask_price_header->setStyleSheet("color: #ff0000; font-weight: bold;");
    auto* ask_volume_header = new QLabel("卖量", this);
    ask_volume_header->setStyleSheet("color: #ff0000; font-weight: bold;");

    grid_layout->addWidget(bid_price_header, 0, 0);
    grid_layout->addWidget(bid_volume_header, 0, 1);
    grid_layout->addWidget(ask_price_header, 0, 2);
    grid_layout->addWidget(ask_volume_header, 0, 3);

    // 初始化10档标签
    for (int i = 0; i < 10; ++i) {
        auto* bid_price_label = new QLabel("--", this);
        bid_price_label->setStyleSheet("color: #00ff00; font-family: monospace;");
        m_bid_price_labels.append(bid_price_label);

        auto* bid_volume_label = new QLabel("--", this);
        bid_volume_label->setStyleSheet("color: #cccccc; font-family: monospace;");
        m_bid_volume_labels.append(bid_volume_label);

        auto* ask_price_label = new QLabel("--", this);
        ask_price_label->setStyleSheet("color: #ff0000; font-family: monospace;");
        m_ask_price_labels.append(ask_price_label);

        auto* ask_volume_label = new QLabel("--", this);
        ask_volume_label->setStyleSheet("color: #cccccc; font-family: monospace;");
        m_ask_volume_labels.append(ask_volume_label);

        grid_layout->addWidget(bid_price_label, i + 1, 0);
        grid_layout->addWidget(bid_volume_label, i + 1, 1);
        grid_layout->addWidget(ask_price_label, i + 1, 2);
        grid_layout->addWidget(ask_volume_label, i + 1, 3);
    }

    main_layout->addLayout(grid_layout);
    main_layout->addStretch();
}

void OrderBookWidget::set_symbol(const QString& symbol) {
    m_symbol = symbol;
    m_symbol_label->setText(QString("Symbol: %1").arg(symbol));

    // 订阅Level 2数据
    auto& level2_service = services::Level2DataService::instance();
    level2_service.subscribe_depth(symbol, [this](const services::Level2Depth& depth) {
        QMetaObject::invokeMethod(this, [this, depth]() {
            on_depth_updated(m_symbol, depth);
        }, Qt::QueuedConnection);
    });

    // 立即刷新一次
    refresh();
}

void OrderBookWidget::refresh() {
    if (m_symbol.isEmpty()) {
        return;
    }

    auto& level2_service = services::Level2DataService::instance();
    auto result = level2_service.get_depth(m_symbol);

    if (result.is_ok()) {
        on_depth_updated(m_symbol, result.value());
    } else {
        LOG_WARN("OrderBook", QString("Failed to get depth for %1: %2").arg(m_symbol).arg(result.error()));
    }
}

void OrderBookWidget::on_depth_updated(const QString& /*symbol*/, const services::Level2Depth& depth) {
    m_current_depth = depth;

    // 更新买盘
    render_bids(depth.bids);

    // 更新卖盘
    render_asks(depth.asks);

    // 更新统计信息
    update_statistics(depth);

    // 触发重绘
    update();
}

void OrderBookWidget::render_bids(const QVector<services::Level2Order>& bids) {
    for (int i = 0; i < 10; ++i) {
        if (i < bids.size()) {
            m_bid_price_labels[i]->setText(QString::number(bids[i].price, 'f', 2));
            m_bid_volume_labels[i]->setText(QString::number(bids[i].volume));
        } else {
            m_bid_price_labels[i]->setText("--");
            m_bid_volume_labels[i]->setText("--");
        }
    }
}

void OrderBookWidget::render_asks(const QVector<services::Level2Order>& asks) {
    for (int i = 0; i < 10; ++i) {
        if (i < asks.size()) {
            m_ask_price_labels[i]->setText(QString::number(asks[i].price, 'f', 2));
            m_ask_volume_labels[i]->setText(QString::number(asks[i].volume));
        } else {
            m_ask_price_labels[i]->setText("--");
            m_ask_volume_labels[i]->setText("--");
        }
    }
}

void OrderBookWidget::update_statistics(const services::Level2Depth& depth) {
    m_bid_avg_label->setText(QString::number(depth.bid_weighted_avg, 'f', 2));
    m_ask_avg_label->setText(QString::number(depth.ask_weighted_avg, 'f', 2));
    m_bid_total_label->setText(QString::number(depth.total_bid_volume));
    m_ask_total_label->setText(QString::number(depth.total_ask_volume));
}

void OrderBookWidget::paintEvent(QPaintEvent* event) {
    QPainter painter(this);
    painter.fillRect(rect(), QColor("#1e1e1e"));  // 深色背景
    QWidget::paintEvent(event);
}

} // namespace fincept::ui
