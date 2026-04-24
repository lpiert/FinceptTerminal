#include "ui/widgets/BacktestWidget.h"
#include "core/logging/Logger.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QFormLayout>
#include <QGroupBox>
#include <QPainter>
#include <QMessageBox>

namespace fincept::ui {

BacktestWidget::BacktestWidget(QWidget* parent)
    : QWidget(parent) {
    setup_ui();

    LOG_INFO("Backtest", "BacktestWidget created");
}

void BacktestWidget::setup_ui() {
    auto* main_layout = new QVBoxLayout(this);
    main_layout->setSpacing(8);
    main_layout->setContentsMargins(12, 12, 12, 12);

    // === Parameters Group ===
    auto* params_group = new QGroupBox("Backtest Parameters", this);
    auto* form_layout = new QFormLayout(params_group);

    // Symbol input
    m_symbol_input = new QLineEdit(this);
    m_symbol_input->setPlaceholderText("e.g., 600519.SS");
    m_symbol_input->setText("600519.SS");
    form_layout->addRow("Symbol:", m_symbol_input);

    // Start date
    m_start_date_edit = new QDateEdit(this);
    m_start_date_edit->setDate(QDate::currentDate().addYears(-1));
    m_start_date_edit->setCalendarPopup(true);
    m_start_date_edit->setDisplayFormat("yyyy-MM-dd");
    form_layout->addRow("Start Date:", m_start_date_edit);

    // End date
    m_end_date_edit = new QDateEdit(this);
    m_end_date_edit->setDate(QDate::currentDate());
    m_end_date_edit->setCalendarPopup(true);
    m_end_date_edit->setDisplayFormat("yyyy-MM-dd");
    form_layout->addRow("End Date:", m_end_date_edit);

    // Strategy selection
    m_strategy_combo = new QComboBox(this);
    m_strategy_combo->addItem("Moving Average Crossover", "ma_cross");
    m_strategy_combo->addItem("RSI Mean Reversion", "rsi");
    m_strategy_combo->addItem("Bollinger Bands Breakout", "bollinger");
    form_layout->addRow("Strategy:", m_strategy_combo);

    // Initial cash
    m_cash_input = new QLineEdit(this);
    m_cash_input->setText("100000");
    m_cash_input->setPlaceholderText("100000");
    form_layout->addRow("Initial Cash (CNY):", m_cash_input);

    main_layout->addWidget(params_group);

    // === Run Button ===
    m_run_btn = new QPushButton("Run Backtest", this);
    m_run_btn->setStyleSheet(
        "QPushButton { background-color: #0066cc; color: white; font-weight: bold; padding: 10px; }"
        "QPushButton:hover { background-color: #0077dd; }"
        "QPushButton:pressed { background-color: #0055aa; }"
        "QPushButton:disabled { background-color: #444444; color: #888888; }"
    );
    connect(m_run_btn, &QPushButton::clicked, this, &BacktestWidget::on_run_backtest);
    main_layout->addWidget(m_run_btn);

    // === Results Display ===
    auto* results_group = new QGroupBox("Results", this);
    auto* results_layout = new QVBoxLayout(results_group);

    m_results_display = new QTextEdit(this);
    m_results_display->setReadOnly(true);
    m_results_display->setStyleSheet(
        "QTextEdit { background-color: #1e1e1e; color: #cccccc; font-family: monospace; font-size: 12px; }"
    );
    results_layout->addWidget(m_results_display);

    main_layout->addWidget(results_group);

    // === Status Label ===
    m_status_label = new QLabel("Ready", this);
    m_status_label->setStyleSheet("color: #aaaaaa; font-style: italic;");
    main_layout->addWidget(m_status_label);

    main_layout->addStretch();
}

void BacktestWidget::on_run_backtest() {
    // Validate inputs
    QString symbol = m_symbol_input->text().trimmed();
    if (symbol.isEmpty()) {
        QMessageBox::warning(this, "Input Error", "Please enter a stock symbol");
        return;
    }

    QString start_date = m_start_date_edit->date().toString("yyyy-MM-dd");
    QString end_date = m_end_date_edit->date().toString("yyyy-MM-dd");
    QString strategy = m_strategy_combo->currentData().toString();
    double initial_cash = m_cash_input->text().toDouble();

    // Disable run button during backtest
    m_run_btn->setEnabled(false);
    m_status_label->setText("Running backtest...");
    clear_results();

    LOG_INFO("Backtest",
             QString("Starting backtest: %1 from %2 to %3")
                 .arg(symbol).arg(start_date).arg(end_date));

    // Run backtest
    auto& service = services::BacktestService::instance();
    service.run_backtest(symbol, start_date, end_date, strategy, initial_cash,
                         [this](const services::BacktestResult& result) {
        QMetaObject::invokeMethod(this, [this, result]() {
            on_backtest_finished(result);
        }, Qt::QueuedConnection);
    });
}

void BacktestWidget::on_backtest_finished(const services::BacktestResult& result) {
    m_run_btn->setEnabled(true);

    if (!result.success) {
        m_status_label->setText(QString("Error: %1").arg(result.error));
        QMessageBox::critical(this, "Backtest Failed", result.error);
        return;
    }

    m_status_label->setText("Backtest completed successfully");
    display_results(result);
}

void BacktestWidget::display_results(const services::BacktestResult& result) {
    QString html = QString(
        "<html><body style='color: #cccccc; font-family: monospace;'>"
        "<h2 style='color: #ffffff;'>Backtest Results</h2>"
        "<table style='width: 100%;'>"
        "<tr><td style='color: #aaaaaa;'>Symbol:</td><td>%1</td></tr>"
        "<tr><td style='color: #aaaaaa;'>Period:</td><td>%2</td></tr>"
        "<tr><td style='color: #aaaaaa;'>Initial Cash:</td><td>¥%3</td></tr>"
        "<tr><td style='color: #aaaaaa;'>Final Value:</td><td style='color: #00ff00; font-weight: bold;'>¥%4</td></tr>"
        "<tr><td style='color: #aaaaaa;'>Total Return:</td><td style='color: %5; font-weight: bold;'>%6%</td></tr>"
        "<tr><td style='color: #aaaaaa;'>Annualized Return:</td><td>%7%</td></tr>"
        "<tr><td style='color: #aaaaaa;'>Sharpe Ratio:</td><td>%8</td></tr>"
        "<tr><td style='color: #aaaaaa;'>Max Drawdown:</td><td style='color: #ff0000;'>%9%</td></tr>"
        "<tr><td style='color: #aaaaaa;'>Total Trades:</td><td>%10</td></tr>"
        "<tr><td style='color: #aaaaaa;'>Winning Trades:</td><td style='color: #00ff00;'>%11</td></tr>"
        "<tr><td style='color: #aaaaaa;'>Losing Trades:</td><td style='color: #ff0000;'>%12</td></tr>"
        "<tr><td style='color: #aaaaaa;'>Win Rate:</td><td>%13%</td></tr>"
        "</table>"
        "</body></html>"
    )
    .arg(result.symbol)
    .arg(result.period)
    .arg(result.initial_cash, 0, 'f', 2)
    .arg(result.final_value, 0, 'f', 2)
    .arg(result.total_return_pct >= 0 ? "#00ff00" : "#ff0000")
    .arg(result.total_return_pct, 0, 'f', 2)
    .arg(result.annualized_return_pct, 0, 'f', 2)
    .arg(result.sharpe_ratio, 0, 'f', 3)
    .arg(result.max_drawdown_pct, 0, 'f', 2)
    .arg(result.total_trades)
    .arg(result.winning_trades)
    .arg(result.losing_trades)
    .arg(result.win_rate_pct, 0, 'f', 2);

    m_results_display->setHtml(html);
}

void BacktestWidget::clear_results() {
    m_results_display->clear();
}

void BacktestWidget::paintEvent(QPaintEvent* event) {
    QPainter painter(this);
    painter.fillRect(rect(), QColor("#1e1e1e"));
    QWidget::paintEvent(event);
}

} // namespace fincept::ui
