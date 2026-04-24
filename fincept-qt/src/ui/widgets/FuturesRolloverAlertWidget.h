#pragma once
#include "trading/FuturesRolloverManager.h"
#include <QWidget>
#include <QLabel>
#include <QPushButton>
#include <QTimer>

namespace fincept::ui {

/// Futures Rollover Alert Widget - 期货合约换月提示
///
/// 监控主力合约状态，当检测到需要换月时：
/// 1. 显示醒目的提示横幅
/// 2. 提供"立即切换"按钮
/// 3. 提供"稍后提醒"按钮
///
/// UI团队可以立即开发，后续接入真实换月逻辑无需修改UI
class FuturesRolloverAlertWidget : public QWidget {
    Q_OBJECT
public:
    explicit FuturesRolloverAlertWidget(QWidget* parent = nullptr);
    ~FuturesRolloverAlertWidget() override = default;

    /// 注册要监控的品种
    void watch_contract(const QString& base_symbol, const QString& exchange);

    /// 隐藏提示
    void hide_alert();

signals:
    /// 用户点击"立即切换"时发出
    void rollover_confirmed(const QString& base_symbol,
                            const QString& old_contract,
                            const QString& new_contract);

    /// 用户点击"稍后提醒"时发出
    void rollover_postponed(const QString& base_symbol);

private slots:
    /// 检查换月状态
    void check_rollover_status();

    /// 处理立即切换按钮
    void on_confirm_rollover();

    /// 处理稍后提醒按钮
    void on_postpone_rollover();

private:
    /// 初始化UI
    void setup_ui();

    /// 显示换月提示
    void show_rollover_alert(const QString& base_symbol,
                             const QString& old_contract,
                             const QString& new_contract);

    // UI元素
    QLabel* m_alert_icon = nullptr;
    QLabel* m_message_label = nullptr;
    QPushButton* m_confirm_btn = nullptr;
    QPushButton* m_postpone_btn = nullptr;

    // 当前换月信息
    QString m_current_base_symbol;
    QString m_old_contract;
    QString m_new_contract;

    // 定时器（每小时检查一次）
    QTimer* m_check_timer = nullptr;

    // 是否正在显示提示
    bool m_alert_visible = false;
};

} // namespace fincept::ui
