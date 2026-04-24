#pragma once

#include "services/polymarket/PolymarketTypes.h"

#include <QComboBox>
#include <QEvent>
#include <QLabel>
#include <QLineEdit>
#include <QPushButton>
#include <QWidget>

namespace fincept::screens::polymarket {

/// Top command bar: view pills, category filters, search, sort, refresh, WS status.
class PolymarketCommandBar : public QWidget {
    Q_OBJECT
  public:
    explicit PolymarketCommandBar(QWidget* parent = nullptr);

    void set_categories(const QVector<services::polymarket::Tag>& tags);
    void set_active_view(const QString& view);
    void set_active_category(const QString& cat);
    void set_loading(bool loading);
    void set_ws_status(bool connected);
    void set_market_count(int count);
    void set_search_text(const QString& text) { if (search_input_) search_input_->setText(text); }
    QString search_text() const { return search_input_ ? search_input_->text() : QString(); }

    /// Populate the exchange dropdown. `ids` are adapter ids from
    /// PredictionExchangeRegistry (e.g. ["polymarket", "kalshi"]); `labels`
    /// are the corresponding display names. The selected entry controls
    /// which adapter the screen pulls data from.
    void set_exchanges(const QStringList& ids, const QStringList& labels, const QString& active_id);

    /// Update the account chip shown next to the exchange combo.
    /// `connected == false` renders "鈿?No account" (clickable CTA);
    /// `connected == true` renders "馃煝 <label>" in green.
    void set_account_status(bool connected, const QString& label);

  signals:
    void view_changed(const QString& view);
    void category_changed(const QString& category);
    void search_submitted(const QString& query);
    void sort_changed(const QString& sort_by);
    void refresh_clicked();

  protected:
    void changeEvent(QEvent* event) override;

  private:
    void build_ui();
    void rebuild_view_pills();
    void apply_accent();
    void rebuild_categories();  // called when presentation or tag set changes
    void retranslateUi();

    QList<QPushButton*> view_btns_;
    QWidget* category_container_ = nullptr;
    QLineEdit* search_input_ = nullptr;
    QComboBox* sort_combo_ = nullptr;
    QPushButton* refresh_btn_ = nullptr;
    QLabel* ws_indicator_ = nullptr;
    QLabel* count_label_ = nullptr;
    QString active_view_ = "MARKETS";
    QString active_category_ = "ALL";

    ExchangePresentation presentation_ = ExchangePresentation::for_polymarket();
    QStringList current_tags_;
    bool ws_connected_ = false;
    bool account_connected_ = false;
    QString account_label_;
};

} // namespace fincept::screens::polymarket
