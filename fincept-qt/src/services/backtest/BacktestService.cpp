#include "services/backtest/BacktestService.h"
#include "python/PythonRunner.h"
#include "core/logging/Logger.h"
#include <QJsonDocument>
#include <QJsonObject>

namespace fincept::services {

BacktestService& BacktestService::instance() {
    static BacktestService s;
    return s;
}

void BacktestService::run_backtest(const QString& symbol,
                                    const QString& start_date,
                                    const QString& end_date,
                                    const QString& strategy,
                                    double initial_cash,
                                    std::function<void(const BacktestResult&)> callback) {
    QStringList args;
    args << "--symbol" << symbol
         << "--start" << start_date
         << "--end" << end_date
         << "--strategy" << strategy
         << "--cash" << QString::number(initial_cash);

    LOG_INFO("Backtest",
             QString("Starting backtest: %1 from %2 to %3 (strategy: %4)")
                 .arg(symbol).arg(start_date).arg(end_date).arg(strategy));

    PythonRunner::instance().run("backtest_engine.py", args,
                                  [callback](PythonRunner::PythonResult result) {
        if (!result.success) {
            LOG_ERROR("Backtest", QString("Backtest failed: %1").arg(result.error));
            BacktestResult error_result;
            error_result.success = false;
            error_result.error = result.error;
            callback(error_result);
            return;
        }

        // Parse result
        auto service = &BacktestService::instance();
        BacktestResult backtest_result = service->parse_result(result.output);

        if (backtest_result.success) {
            LOG_INFO("Backtest",
                     QString("Backtest completed: Return=%1%, Sharpe=%2, Trades=%3")
                         .arg(backtest_result.total_return_pct, 0, 'f', 2)
                         .arg(backtest_result.sharpe_ratio, 0, 'f', 3)
                         .arg(backtest_result.total_trades));
        } else {
            LOG_ERROR("Backtest", QString("Backtest error: %1").arg(backtest_result.error));
        }

        callback(backtest_result);
    });
}

QStringList BacktestService::available_strategies() const {
    return {"ma_cross", "rsi", "bollinger"};
}

BacktestResult BacktestService::parse_result(const QString& json_output) {
    BacktestResult result;

    try {
        auto doc = QJsonDocument::fromJson(json_output.toUtf8());
        if (!doc.isObject()) {
            result.error = "Invalid JSON response";
            return result;
        }

        auto obj = doc.object();
        result.success = obj["success"].toBool();

        if (!result.success) {
            result.error = obj["error"].toString();
            return result;
        }

        result.symbol = obj["symbol"].toString();
        result.period = obj["period"].toString();
        result.initial_cash = obj["initial_cash"].toDouble();
        result.final_value = obj["final_value"].toDouble();
        result.total_return_pct = obj["total_return"].toDouble();
        result.sharpe_ratio = obj["sharpe_ratio"].toDouble();
        result.max_drawdown_pct = obj["max_drawdown"].toDouble();
        result.total_trades = obj["total_trades"].toInt();
        result.winning_trades = obj["winning_trades"].toInt();
        result.losing_trades = obj["losing_trades"].toInt();
        result.win_rate_pct = obj["win_rate"].toDouble();
        result.annualized_return_pct = obj["annualized_return"].toDouble();

    } catch (const std::exception& e) {
        result.error = QString("Parse error: %1").arg(e.what());
        result.success = false;
    }

    return result;
}

} // namespace fincept::services
