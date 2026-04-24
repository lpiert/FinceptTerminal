#pragma once

#include "services/polymarket/PolymarketTypes.h"

#include <QComboBox>
#include <QEvent>
#include <QLabel>
#include <QPushButton>
#include <QWidget>

namespace fincept::screens::polymarket {

/// Price chart with interval selector and outcome toggle.
class PolymarketPriceChart : public QWidget {
    Q_OBJECT
  public:
    explicit PolymarketPriceChart(QWidget* parent = nullptr);

    void set_price_history(const services::polymarket::PriceHistory& history);
    void set_current_price(double price);
    void set_token_labels(const QStringList& labels);

  signals:
    void interval_changed(const QString& interval);
    void outcome_changed(int index);

  protected:
    void changeEvent(QEvent* event) override;

  private:
    void retranslateUi();

    QWidget* chart_container_ = nullptr;
    QComboBox* interval_combo_ = nullptr;
    QComboBox* outcome_combo_ = nullptr;
    QLabel* price_label_ = nullptr;
    QLabel* interval_lbl_ = nullptr;
    QLabel* outcome_lbl_ = nullptr;

    // Cached last history so set_presentation() can re-render.
    fincept::services::prediction::PriceHistory last_history_;
    bool has_last_history_ = false;

    ExchangePresentation presentation_ = ExchangePresentation::for_polymarket();
};

} // namespace fincept::screens::polymarket
