#include "ui/widgets/TradingPanelWidget.h"
#include "trading/BrokerRegistry.h"
#include "core/logging/Logger.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QFormLayout>
#include <QGroupBox>
#include <QMessageBox>
#include <QPainter>

namespace fincept::ui {

TradingPanelWidget::TradingPanelWidget(QWidget* parent)
    : QWidget(parent) {
    setup_ui();
    load_brokers();

    LOG_INFO("TradingPanel", "TradingPanelWidget created (using stub brokers)");
}

void TradingPanelWidget::setup_ui() {
    auto* main_layout = new QVBoxLayout(this);
    main_layout->setSpacing(8);
    main_layout->setContentsMargins(12, 12, 12, 12);

    // === 账户选择区域 ===
    auto* account_group = new QGroupBox("交易账户", this);
    auto* account_layout = new QHBoxLayout(account_group);

    account_layout->addWidget(new QLabel("券商:", this));
    m_broker_combo = new QComboBox(this);
    account_layout->addWidget(m_broker_combo);

    connect(m_broker_combo, QOverload<int>::of(&QComboBox::currentIndexChanged),
            [this](int index) {
                if (index >= 0) {
                    m_current_broker_id = m_broker_combo->itemData(index).toString();
                    update_account_info();
                }
            });

    main_layout->addWidget(account_group);

    // === 交易参数输入区域 ===
    auto* order_group = new QGroupBox("下单参数", this);
    auto* form_layout = new QFormLayout(order_group);

    // Symbol输入
    m_symbol_input = new QLineEdit(this);
    m_symbol_input->setPlaceholderText("例如: 600519.SS");
    form_layout->addRow("股票代码:", m_symbol_input);

    // 买卖方向
    m_side_combo = new QComboBox(this);
    m_side_combo->addItem("买入", "buy");
    m_side_combo->addItem("卖出", "sell");
    form_layout->addRow("方向:", m_side_combo);

    // 订单类型
    m_type_combo = new QComboBox(this);
    m_type_combo->addItem("限价委托", "limit");
    m_type_combo->addItem("市价委托", "market");
    form_layout->addRow("类型:", m_type_combo);

    // 价格输入
    m_price_input = new QLineEdit(this);
    m_price_input->setPlaceholderText("0.00");
    form_layout->addRow("价格:", m_price_input);

    // 数量输入
    m_quantity_input = new QLineEdit(this);
    m_quantity_input->setPlaceholderText("0");
    form_layout->addRow("数量:", m_quantity_input);

    main_layout->addWidget(order_group);

    // === 账户信息区域 ===
    auto* info_group = new QGroupBox("账户信息", this);
    auto* info_layout = new QVBoxLayout(info_group);

    auto* funds_layout = new QHBoxLayout();
    funds_layout->addWidget(new QLabel("可用资金:", this));
    m_available_funds_label = new QLabel("--", this);
    m_available_funds_label->setStyleSheet("color: #00ff00; font-weight: bold;");
    funds_layout->addWidget(m_available_funds_label);
    funds_layout->addStretch();
    info_layout->addLayout(funds_layout);

    auto* position_layout = new QHBoxLayout();
    position_layout->addWidget(new QLabel("当前持仓:", this));
    m_position_label = new QLabel("--", this);
    m_position_label->setStyleSheet("color: #ffff00;");
    position_layout->addWidget(m_position_label);
    position_layout->addStretch();
    info_layout->addLayout(position_layout);

    main_layout->addWidget(info_group);

    // === 操作按钮区域 ===
    auto* btn_layout = new QHBoxLayout();

    m_place_order_btn = new QPushButton("下单", this);
    m_place_order_btn->setStyleSheet(
        "QPushButton { background-color: #00aa00; color: white; font-weight: bold; padding: 8px; }"
        "QPushButton:hover { background-color: #00cc00; }"
        "QPushButton:pressed { background-color: #008800; }"
    );
    connect(m_place_order_btn, &QPushButton::clicked, this, &TradingPanelWidget::on_place_order);
    btn_layout->addWidget(m_place_order_btn);

    m_cancel_order_btn = new QPushButton("撤单", this);
    m_cancel_order_btn->setStyleSheet(
        "QPushButton { background-color: #aa0000; color: white; font-weight: bold; padding: 8px; }"
        "QPushButton:hover { background-color: #cc0000; }"
        "QPushButton:pressed { background-color: #880000; }"
    );
    connect(m_cancel_order_btn, &QPushButton::clicked, this, &TradingPanelWidget::on_cancel_order);
    btn_layout->addWidget(m_cancel_order_btn);

    main_layout->addLayout(btn_layout);

    // === 状态显示区域 ===
    m_status_label = new QLabel("就绪", this);
    m_status_label->setStyleSheet("color: #aaaaaa; font-style: italic;");
    main_layout->addWidget(m_status_label);

    main_layout->addStretch();
}

void TradingPanelWidget::set_symbol(const QString& symbol) {
    m_symbol_input->setText(symbol);
}

void TradingPanelWidget::set_broker_id(const QString& broker_id) {
    m_current_broker_id = broker_id;

    // 更新下拉框选择
    for (int i = 0; i < m_broker_combo->count(); ++i) {
        if (m_broker_combo->itemData(i).toString() == broker_id) {
            m_broker_combo->setCurrentIndex(i);
            break;
        }
    }
}

void TradingPanelWidget::load_brokers() {
    // TODO: 从 BrokerRegistry 加载所有已注册的broker
    // 当前添加几个示例broker用于UI开发

    m_broker_combo->clear();

    // 添加桩代码broker
    m_broker_combo->addItem("CTP期货", "ctp");
    m_broker_combo->addItem("XTP股票", "xtp");

    // 添加已有的broker（如果已注册）
    auto& registry = trading::BrokerRegistry::instance();
    for (const auto& broker : registry.all_brokers()) {
        m_broker_combo->addItem(broker->name(), QString::fromStdString(broker->id()));
    }

    LOG_INFO("TradingPanel", QString("Loaded %1 brokers").arg(m_broker_combo->count()));
}

void TradingPanelWidget::update_account_info() {
    // TODO: 从broker获取真实账户信息
    // 当前显示模拟数据

    m_available_funds_label->setText("¥ 1,000,000.00 (模拟)");
    m_position_label->setText("0 股");

    LOG_INFO("TradingPanel", "Account info updated (mock data)");
}

bool TradingPanelWidget::validate_input(QString& error_msg) {
    // 验证symbol
    if (m_symbol_input->text().trimmed().isEmpty()) {
        error_msg = "请输入股票代码";
        return false;
    }

    // 验证价格
    bool price_ok;
    double price = m_price_input->text().toDouble(&price_ok);
    if (!price_ok || price <= 0) {
        error_msg = "请输入有效的价格";
        return false;
    }

    // 验证数量
    bool qty_ok;
    int quantity = m_quantity_input->text().toInt(&qty_ok);
    if (!qty_ok || quantity <= 0) {
        error_msg = "请输入有效的数量";
        return false;
    }

    // A股最小交易单位检查
    if (quantity % 100 != 0) {
        error_msg = "A股交易数量必须是100的整数倍";
        return false;
    }

    return true;
}

void TradingPanelWidget::on_place_order() {
    // 验证输入
    QString error_msg;
    if (!validate_input(error_msg)) {
        QMessageBox::warning(this, "输入错误", error_msg);
        m_status_label->setText(QString("错误: %1").arg(error_msg));
        return;
    }

    // 构建订单
    trading::UnifiedOrder order;
    order.symbol = m_symbol_input->text().trimmed();
    order.side = (m_side_combo->currentData().toString() == "buy")
                     ? trading::OrderSide::Buy
                     : trading::OrderSide::Sell;
    order.type = (m_type_combo->currentData().toString() == "limit")
                     ? trading::OrderType::Limit
                     : trading::OrderType::Market;
    order.price = m_price_input->text().toDouble();
    order.quantity = m_quantity_input->text().toInt();

    // TODO: 调用broker下单
    // 当前显示提示信息
    LOG_WARN("TradingPanel",
             QString("Place order clicked (STUB): %1 %2 %3 @ %4 x %5")
                 .arg(order.symbol)
                 .arg(order.side == trading::OrderSide::Buy ? "BUY" : "SELL")
                 .arg(order.type == trading::OrderType::Limit ? "LIMIT" : "MARKET")
                 .arg(order.price)
                 .arg(order.quantity));

    QMessageBox::information(this, "下单提示",
                             QString("这是桩代码演示\n\n"
                                     "股票代码: %1\n"
                                     "方向: %2\n"
                                     "价格: %3\n"
                                     "数量: %4\n\n"
                                     "实盘功能需要对接CTP/XTP API后才能使用。")
                                 .arg(order.symbol)
                                 .arg(m_side_combo->currentText())
                                 .arg(order.price)
                                 .arg(order.quantity));

    m_status_label->setText("下单功能未实现（桩代码）");

    // 发出失败信号
    emit order_failed("Broker not implemented yet");
}

void TradingPanelWidget::on_cancel_order() {
    QMessageBox::information(this, "撤单提示",
                             "撤单功能需要对接真实Broker后才能使用。\n\n"
                             "请确保已选择正确的券商账户。");

    m_status_label->setText("撤单功能未实现（桩代码）");
}

void TradingPanelWidget::paintEvent(QPaintEvent* event) {
    QPainter painter(this);
    painter.fillRect(rect(), QColor("#1e1e1e"));  // 深色背景
    QWidget::paintEvent(event);
}

} // namespace fincept::ui
