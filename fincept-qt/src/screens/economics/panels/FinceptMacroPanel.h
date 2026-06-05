// src/screens/economics/panels/FinceptMacroPanel.h
// Fincept Macro — FREE MODE: Uses free_macro_aggregator.py
// Aggregates data from World Bank, IMF, FRED, OECD, AKShare, ECB, BIS
// All sources are FREE - no API keys required
#pragma once

#include "screens/economics/panels/EconPanelBase.h"
#include <QComboBox>
#include <QPushButton>

namespace fincept::screens {

class FinceptMacroPanel : public EconPanelBase {
    Q_OBJECT
  public:
    explicit FinceptMacroPanel(QWidget* parent = nullptr);
    void activate() override;

  protected:
    void build_controls(QHBoxLayout* thl) override;
    void on_fetch() override;
    void on_result(const QString& request_id, const services::EconomicsResult& result) override;
    void changeEvent(QEvent* event) override;

  private:
    void display_macro_data(const QJsonObject& data);
    void retranslateUi() override;

    // Cached for retranslateUi
    QLabel* coming_soon_lbl_ = nullptr;
    QString selected_country_ = "US";};

} // namespace fincept::screens
