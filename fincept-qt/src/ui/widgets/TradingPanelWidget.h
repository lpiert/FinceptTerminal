#pragma once
#include "trading/BrokerInterface.h"
#include <QWidget>
#include <QComboBox>
#include <QLineEdit>
#include <QPushButton>
#include <QLabel>

namespace fincept::ui {

/// Trading Panel Widget - 交易下单面板
///
/// 提供完整的下单界面：
/// - 选择券商/账户
/// - 输入股票代码、价格、数量
/// - 选择买卖方向、订单类型
/// - 显示可用资金、可卖数量
///
/// 当前基于桩代码Broker，点击"下单"会返回"Not Implemented"错误
/// UI团队可以完整开发界面布局、验证逻辑、错误提示等
class TradingPanelWidget : public QWidget {
    Q_OBJECT
public:
    explicit TradingPanelWidget(QWidget* parent = nullptr);
    ~TradingPanelWidget() override = default;

    /// 设置当前交易的symbol
    void set_symbol(const QString& symbol);

    /// 设置当前券商ID
    void set_broker_id(const QString& broker_id);

signals:
    /// 下单成功信号
    void order_placed(const QString& order_id);

    /// 下单失败信号
    void order_failed(const QString& error);

private slots:
    /// 处理下单按钮点击
    void on_place_order();

    /// 处理撤单按钮点击
    void on_cancel_order();

    /// 更新可用资金和持仓
    void update_account_info();

private:
    /// 初始化UI布局
    void setup_ui();

    /// 验证输入
    bool validate_input(QString& error_msg);

    /// 加载券商列表
    void load_brokers();

    // 账户选择
    QComboBox* m_broker_combo = nullptr;

    // 交易参数输入
    QLineEdit* m_symbol_input = nullptr;
    QComboBox* m_side_combo = nullptr;      // 买/卖
    QComboBox* m_type_combo = nullptr;      // 限价/市价
    QLineEdit* m_price_input = nullptr;
    QLineEdit* m_quantity_input = nullptr;

    // 账户信息显示
    QLabel* m_available_funds_label = nullptr;
    QLabel* m_position_label = nullptr;

    // 操作按钮
    QPushButton* m_place_order_btn = nullptr;
    QPushButton* m_cancel_order_btn = nullptr;

    // 状态标签
    QLabel* m_status_label = nullptr;

    // 当前broker
    QString m_current_broker_id;
};

} // namespace fincept::ui
