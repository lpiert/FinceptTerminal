#include "screens/polymarket/PolymarketPriceChart.h"

#include "ui/charts/ChartFactory.h"
#include "ui/theme/Theme.h"

#include <QHBoxLayout>
#include <QVBoxLayout>

namespace fincept::screens::polymarket {

using namespace fincept::ui;
using namespace fincept::services::polymarket;

static const QStringList INTERVAL_VALUES = {"1h", "6h", "1d", "1w", "1m", "max"};

PolymarketPriceChart::PolymarketPriceChart(QWidget* parent) : QWidget(parent) {
    auto* vl = new QVBoxLayout(this);
    vl->setContentsMargins(8, 8, 8, 8);
    vl->setSpacing(4);

    auto* toolbar = new QHBoxLayout;
    toolbar->setSpacing(6);

    interval_lbl_ = new QLabel(tr("INTERVAL"));
    auto* lbl = interval_lbl_;
    lbl->setStyleSheet(
        QString("color: %1; font-size: 9px; font-weight: 700; background: transparent;").arg(colors::TEXT_SECONDARY()));
    toolbar->addWidget(lbl);

    interval_combo_ = new QComboBox;
    interval_combo_->addItems({tr("1H"), tr("6H"), tr("1D"), tr("1W"), tr("1M"), tr("ALL")});
    interval_combo_->setCurrentIndex(2);
    interval_combo_->setFixedSize(62, 24);
    interval_combo_->setStyleSheet(combo_css);
    connect(interval_combo_, QOverload<int>::of(&QComboBox::currentIndexChanged), this, [this](int idx) {
        if (idx >= 0 && idx < INTERVAL_VALUES.size())
            emit interval_changed(INTERVAL_VALUES[idx]);
    });
    toolbar->addWidget(interval_combo_);

    toolbar->addSpacing(12);

    outcome_lbl_ = new QLabel(tr("OUTCOME"));
    auto* olbl = outcome_lbl_;
    olbl->setStyleSheet(lbl->styleSheet());
    toolbar->addWidget(olbl);

    outcome_combo_ = new QComboBox;
    outcome_combo_->addItems({"YES", "NO"});
    outcome_combo_->setFixedWidth(70);
    connect(outcome_combo_, QOverload<int>::of(&QComboBox::currentIndexChanged), this,
            &PolymarketPriceChart::outcome_changed);
    toolbar->addWidget(outcome_combo_);

    toolbar->addStretch(1);

    price_label_ = new QLabel;
    price_label_->setStyleSheet(
        QString("color: %1; font-size: 13px; font-weight: 700; background: transparent;").arg(colors::AMBER()));
    toolbar->addWidget(price_label_);

    vl->addLayout(toolbar);

    chart_container_ = new QWidget(this);
    auto* ccl = new QVBoxLayout(chart_container_);
    ccl->setContentsMargins(8, 8, 8, 8);
    auto* empty = new QLabel(tr("Select a market to view its price chart"));
    empty->setStyleSheet(
        QString("color: %1; font-size: 12px; background: transparent;").arg(colors::TEXT_DIM()));
    empty->setAlignment(Qt::AlignCenter);
    ccl->addWidget(empty);
    vl->addWidget(chart_container_, 1);
}

void PolymarketPriceChart::set_price_history(const PriceHistory& history) {
    auto* layout = chart_container_->layout();
    while (layout->count() > 0) {
        auto* item = layout->takeAt(0);
        if (item->widget())
            item->widget()->deleteLater();
        delete item;
    }

    if (history.points.isEmpty()) {
        auto* empty = new QLabel(tr("No price history available"));
        empty->setStyleSheet(QString("color: %1; font-size: 13px; background: transparent;").arg(colors::TEXT_DIM()));
        empty->setAlignment(Qt::AlignCenter);
        layout->addWidget(empty);
        return;
    }

    QVector<ChartFactory::DataPoint> data;
    data.reserve(history.points.size());
    for (const auto& pt : history.points) {
        data.append({static_cast<double>(pt.timestamp), pt.price * 100.0}); // scale to cents
    }

    auto* chart_view = ChartFactory::line_chart("PROBABILITY", data, colors::AMBER);
    layout->addWidget(chart_view);
}

void PolymarketPriceChart::set_current_price(double price) {
    price_label_->setText(QString("%1c").arg(qRound(price * 100)));
}

void PolymarketPriceChart::set_token_labels(const QStringList& labels) {
    outcome_combo_->clear();
    outcome_combo_->addItems(labels);
}

void PolymarketPriceChart::changeEvent(QEvent* event) {
    if (event->type() == QEvent::LanguageChange)
        retranslateUi();
    QWidget::changeEvent(event);
}

void PolymarketPriceChart::retranslateUi() {
    if (interval_lbl_) interval_lbl_->setText(tr("INTERVAL"));
    if (outcome_lbl_)  outcome_lbl_->setText(tr("OUTCOME"));
    if (interval_combo_) {
        const QSignalBlocker block(interval_combo_);
        const int idx = interval_combo_->currentIndex();
        const QStringList labels = {tr("1H"), tr("6H"), tr("1D"), tr("1W"), tr("1M"), tr("ALL")};
        for (int i = 0; i < interval_combo_->count() && i < labels.size(); ++i)
            interval_combo_->setItemText(i, labels[i]);
        interval_combo_->setCurrentIndex(idx);
    }
    // Outcome combo items are market outcome names (data) 鈥?not retranslated.
    // The empty-state placeholder re-renders via set_price_history().
    if (has_last_history_) set_price_history(last_history_);
}

} // namespace fincept::screens::polymarket
