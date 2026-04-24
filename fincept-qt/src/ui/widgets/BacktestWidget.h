#pragma once
#include "services/backtest/BacktestService.h"
#include <QWidget>
#include <QComboBox>
#include <QLineEdit>
#include <QDateEdit>
#include <QPushButton>
#include <QLabel>
#include <QTextEdit>

namespace fincept::ui {

/// Backtest Widget - Strategy backtesting UI
///
/// Provides interface to configure and run backtests
/// Displays results with key metrics (return, Sharpe, drawdown, etc.)
class BacktestWidget : public QWidget {
    Q_OBJECT
public:
    explicit BacktestWidget(QWidget* parent = nullptr);
    ~BacktestWidget() override = default;

private slots:
    /// Run backtest with current parameters
    void on_run_backtest();

    /// Handle backtest completion
    void on_backtest_finished(const services::BacktestResult& result);

private:
    /// Initialize UI layout
    void setup_ui();

    /// Display backtest results
    void display_results(const services::BacktestResult& result);

    /// Clear results display
    void clear_results();

    // Input fields
    QLineEdit* m_symbol_input = nullptr;
    QDateEdit* m_start_date_edit = nullptr;
    QDateEdit* m_end_date_edit = nullptr;
    QComboBox* m_strategy_combo = nullptr;
    QLineEdit* m_cash_input = nullptr;
    QPushButton* m_run_btn = nullptr;

    // Results display
    QTextEdit* m_results_display = nullptr;
    QLabel* m_status_label = nullptr;
};

} // namespace fincept::ui
