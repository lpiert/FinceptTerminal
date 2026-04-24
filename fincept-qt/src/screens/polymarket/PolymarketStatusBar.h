#pragma once

#include <QColor>
#include <QEvent>
#include <QLabel>
#include <QWidget>

namespace fincept::screens::polymarket {

/// Bottom status strip with view info, market count, selection, WS status.
class PolymarketStatusBar : public QWidget {
    Q_OBJECT
  public:
    explicit PolymarketStatusBar(QWidget* parent = nullptr);

    void set_view(const QString& view);
    void set_count(int count, const QString& label);
    void set_selected(const QString& question);
    void set_ws_status(bool connected);

    /// Brand label (left) follows the active exchange. The colour is used
    /// for the brand text and the selected-market highlight.
    void set_brand(const QString& name, const QColor& accent);

    /// Exchange lifecycle (OPEN / PAUSED / CLOSED / MAINT). Empty string
    /// hides the pill 鈥?use this for exchanges that don't expose status.
    void set_exchange_status(const QString& status);

    /// Human-readable "Opens at 鈥? / "Closed" hint pulled from the
    /// exchange schedule. Empty hides the label.
    void set_next_session(const QString& text);

  protected:
    void changeEvent(QEvent* event) override;

  private:
    void retranslateUi();

    QLabel* brand_label_ = nullptr;
    QLabel* view_label_ = nullptr;
    QLabel* count_label_ = nullptr;
    QLabel* selected_label_ = nullptr;
    QLabel* ws_label_ = nullptr;

    QColor accent_{0xD97706};  // default amber 鈥?Polymarket
    bool ws_connected_ = false;
};

} // namespace fincept::screens::polymarket
