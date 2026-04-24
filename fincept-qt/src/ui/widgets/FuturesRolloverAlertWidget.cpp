#include "ui/widgets/FuturesRolloverAlertWidget.h"
#include "core/logging/Logger.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QPainter>
#include <QPainterPath>

namespace fincept::ui {

FuturesRolloverAlertWidget::FuturesRolloverAlertWidget(QWidget* parent)
    : QWidget(parent) {
    setup_ui();

    // 启动定时器，每小时检查一次换月状态
    m_check_timer = new QTimer(this);
    connect(m_check_timer, &QTimer::timeout, this, &FuturesRolloverAlertWidget::check_rollover_status);
    m_check_timer->start(60 * 60 * 1000);  // 1小时

    // 初始检查
    check_rollover_status();

    LOG_INFO("FuturesRollover", "FuturesRolloverAlertWidget created");
}

void FuturesRolloverAlertWidget::setup_ui() {
    auto* main_layout = new QHBoxLayout(this);
    main_layout->setSpacing(12);
    main_layout->setContentsMargins(16, 12, 16, 12);

    // 警告图标
    m_alert_icon = new QLabel("⚠️", this);
    m_alert_icon->setStyleSheet("font-size: 24px;");
    main_layout->addWidget(m_alert_icon);

    // 消息文本
    m_message_label = new QLabel(this);
    m_message_label->setStyleSheet("color: #ffaa00; font-weight: bold; font-size: 13px;");
    m_message_label->setWordWrap(true);
    main_layout->addWidget(m_message_label, 1);

    // 按钮区域
    auto* btn_layout = new QHBoxLayout();
    btn_layout->setSpacing(8);

    m_confirm_btn = new QPushButton("立即切换", this);
    m_confirm_btn->setStyleSheet(
        "QPushButton { background-color: #ff6600; color: white; font-weight: bold; padding: 6px 12px; border-radius: 4px; }"
        "QPushButton:hover { background-color: #ff7700; }"
    );
    connect(m_confirm_btn, &QPushButton::clicked, this, &FuturesRolloverAlertWidget::on_confirm_rollover);
    btn_layout->addWidget(m_confirm_btn);

    m_postpone_btn = new QPushButton("稍后提醒", this);
    m_postpone_btn->setStyleSheet(
        "QPushButton { background-color: #444444; color: white; padding: 6px 12px; border-radius: 4px; }"
        "QPushButton:hover { background-color: #555555; }"
    );
    connect(m_postpone_btn, &QPushButton::clicked, this, &FuturesRolloverAlertWidget::on_postpone_rollover);
    btn_layout->addWidget(m_postpone_btn);

    main_layout->addLayout(btn_layout);

    // 默认隐藏
    hide();
}

void FuturesRolloverAlertWidget::watch_contract(const QString& base_symbol, const QString& exchange) {
    Q_UNUSED(exchange);

    auto& rollover_mgr = trading::FuturesRolloverManager::instance();

    // 注册换月回调
    rollover_mgr.register_callback(base_symbol, [this, base_symbol](const QString& old_c, const QString& new_c) {
        QMetaObject::invokeMethod(this, [this, base_symbol, old_c, new_c]() {
            show_rollover_alert(base_symbol, old_c, new_c);
        }, Qt::QueuedConnection);
    });

    LOG_INFO("FuturesRollover", QString("Watching contract: %1").arg(base_symbol));
}

void FuturesRolloverAlertWidget::hide_alert() {
    hide();
    m_alert_visible = false;
}

void FuturesRolloverAlertWidget::check_rollover_status() {
    // TODO: 定期检查所有监控的合约
    // 当前由FuturesRolloverManager的回调触发

    LOG_DEBUG("FuturesRollover", "Checking rollover status (stub)");
}

void FuturesRolloverAlertWidget::show_rollover_alert(const QString& base_symbol,
                                                      const QString& old_contract,
                                                      const QString& new_contract) {
    m_current_base_symbol = base_symbol;
    m_old_contract = old_contract;
    m_new_contract = new_contract;

    // 更新消息文本
    QString message = QString("<b>期货合约换月提示</b><br>"
                              "品种: %1<br>"
                              "当前合约: <span style='color:#ff0000;'>%2</span> → "
                              "新合约: <span style='color:#00ff00;'>%3</span>")
                          .arg(base_symbol)
                          .arg(old_contract)
                          .arg(new_contract);

    m_message_label->setText(message);

    // 显示提示
    show();
    m_alert_visible = true;

    LOG_INFO("FuturesRollover",
             QString("Rollover alert shown: %1 -> %2").arg(old_contract).arg(new_contract));
}

void FuturesRolloverAlertWidget::on_confirm_rollover() {
    LOG_INFO("FuturesRollover",
             QString("User confirmed rollover: %1 -> %2").arg(m_old_contract).arg(m_new_contract));

    emit rollover_confirmed(m_current_base_symbol, m_old_contract, m_new_contract);

    // 隐藏提示
    hide_alert();
}

void FuturesRolloverAlertWidget::on_postpone_rollover() {
    LOG_INFO("FuturesRollover",
             QString("User postponed rollover for %1").arg(m_current_base_symbol));

    emit rollover_postponed(m_current_base_symbol);

    // 隐藏提示（下次检查时会再次显示）
    hide_alert();
}

void FuturesRolloverAlertWidget::paintEvent(QPaintEvent* event) {
    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);

    // 绘制圆角矩形背景
    QPainterPath path;
    path.addRoundedRect(rect().adjusted(1, 1, -1, -1), 8, 8);

    // 渐变背景色
    QLinearGradient gradient(rect().topLeft(), rect().bottomLeft());
    gradient.setColorAt(0, QColor("#2a2a2a"));
    gradient.setColorAt(1, QColor("#1e1e1e"));

    painter.fillPath(path, gradient);

    // 绘制边框
    QPen pen(QColor("#ffaa00"), 2);
    painter.setPen(pen);
    painter.drawPath(path);

    QWidget::paintEvent(event);
}

} // namespace fincept::ui
