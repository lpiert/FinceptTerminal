#pragma once
#include "core/result/Result.h"
#include <QObject>
#include <QString>
#include <QJsonObject>

namespace fincept::services {

/// Backtest Result Structure
struct BacktestResult {
    bool success = false;
    QString symbol;
    QString period;
    double initial_cash = 0;
    double final_value = 0;
    double total_return_pct = 0;
    double sharpe_ratio = 0;
    double max_drawdown_pct = 0;
    int total_trades = 0;
    int winning_trades = 0;
    int losing_trades = 0;
    double win_rate_pct = 0;
    double annualized_return_pct = 0;
    QString error;
};

/// Backtest Service - Integrates with Python Backtrader engine
///
/// Provides C++ interface to Python backtesting strategies
/// Uses PythonRunner to execute backtests asynchronously
class BacktestService : public QObject {
    Q_OBJECT
public:
    static BacktestService& instance();

    /// Run backtest asynchronously
    ///
    /// @param symbol Stock symbol (e.g., "600519.SS")
    /// @param start_date Start date (YYYY-MM-DD)
    /// @param end_date End date (YYYY-MM-DD)
    /// @param strategy Strategy name ("ma_cross", "rsi", "bollinger")
    /// @param initial_cash Initial capital (default 100,000 CNY)
    /// @param callback Callback function invoked when backtest completes
    void run_backtest(const QString& symbol,
                      const QString& start_date,
                      const QString& end_date,
                      const QString& strategy,
                      double initial_cash,
                      std::function<void(const BacktestResult&)> callback);

    /// Get list of available strategies
    QStringList available_strategies() const;

private:
    BacktestService() = default;

    /// Parse JSON result from Python script
    BacktestResult parse_result(const QString& json_output);
};

} // namespace fincept::services
