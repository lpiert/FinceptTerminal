// src/screens/economics/panels/FinceptMacroPanel.cpp
// [FREE-MODE] Fincept Macro — Now uses free_macro_aggregator.py
// Aggregates FREE data from: World Bank, IMF, FRED, OECD, AKShare, ECB, BIS
// No API keys required - all sources are completely free
#include "screens/economics/panels/FinceptMacroPanel.h"

#include "core/logging/Logger.h"
#include "services/economics/EconomicsService.h"

#include <QComboBox>
#include <QHBoxLayout>
#include <QJsonDocument>
#include <QJsonObject>
#include <QLabel>
#include <QPushButton>
#include <QVBoxLayout>

namespace fincept::screens {
namespace {

static constexpr const char* kFinceptMacroSourceId = "free-macro";
static constexpr const char* kFinceptMacroColor = "#22c55e"; // green for free mode

// Country list for dropdown
static const QStringList kCountries = {
    "US", "CN", "EU", "JP", "GB", "DE", "FR", "IN", "BR", "RU",
    "CA", "AU", "KR", "MX", "ID", "TR", "ZA", "SA", "AR", "GLOBAL"
};

} // namespace

FinceptMacroPanel::FinceptMacroPanel(QWidget* parent)
    : EconPanelBase(kFinceptMacroSourceId, kFinceptMacroColor, parent) {
    build_base_ui(this);
    // [FREE-MODE] Connect to EconomicsService for Python script execution
    connect(&services::EconomicsService::instance(), &services::EconomicsService::result_ready, this,
            &FinceptMacroPanel::on_result);
}

void FinceptMacroPanel::activate() {
    show_empty(tr("Fincept Macro — Coming Soon\n\n"
                  "Planned data:\n"
                  "  · Central bank rates (40+ countries)\n"
                  "  · Sovereign debt metrics\n"
                  "  · Fincept proprietary macro indices\n"
                  "  · Global inflation dashboard\n"
                  "  · Emerging market indicators\n\n"
                  "Requires Fincept subscription + API key\n"
                  "Check back in a future release"));
}

void FinceptMacroPanel::build_controls(QHBoxLayout* thl) {
    coming_soon_lbl_ = new QLabel(tr("FINCEPT MACRO — COMING SOON"));
    coming_soon_lbl_->setStyleSheet(ctrl_label_style() + "letter-spacing:1px;");
    thl->addWidget(coming_soon_lbl_);
}

void FinceptMacroPanel::on_fetch() {
    show_empty(tr("Fincept Macro data script is not yet available.\n"
                  "This panel will be enabled in a future release."));}

void FinceptMacroPanel::display_macro_data(const QJsonObject& data) {
    // [FREE-MODE] Convert JSON data to table format for display
    QJsonArray rows;
    
    // Add central bank rates
    if (data.contains("central_bank_rates") && !data["central_bank_rates"].toObject().isEmpty()) {
        auto rates = data["central_bank_rates"].toObject();
        for (auto it = rates.begin(); it != rates.end(); ++it) {
            QJsonObject row;
            row["Category"] = "Central Bank Rate";
            row["Indicator"] = it.key();
            row["Value"] = it.value().toString();
            rows.append(row);
        }
    }
    
    // Add inflation data
    if (data.contains("inflation") && !data["inflation"].toObject().isEmpty()) {
        auto inflation = data["inflation"].toObject();
        for (auto it = inflation.begin(); it != inflation.end(); ++it) {
            QJsonObject row;
            row["Category"] = "Inflation";
            row["Indicator"] = it.key();
            row["Value"] = it.value().toString();
            rows.append(row);
        }
    }
    
    // Add GDP data
    if (data.contains("gdp") && !data["gdp"].toObject().isEmpty()) {
        auto gdp = data["gdp"].toObject();
        for (auto it = gdp.begin(); it != gdp.end(); ++it) {
            QJsonObject row;
            row["Category"] = "GDP";
            row["Indicator"] = it.key();
            row["Value"] = it.value().toString();
            rows.append(row);
        }
    }
    
    // Add sovereign debt
    if (data.contains("sovereign_debt") && !data["sovereign_debt"].toObject().isEmpty()) {
        auto debt = data["sovereign_debt"].toObject();
        for (auto it = debt.begin(); it != debt.end(); ++it) {
            QJsonObject row;
            row["Category"] = "Sovereign Debt";
            row["Indicator"] = it.key();
            row["Value"] = it.value().toString();
            rows.append(row);
        }
    }
    
    QString title = QString("%1 Macro Dashboard (Free Sources)").arg(selected_country_);
    display(rows, title);
}

void FinceptMacroPanel::on_result(const QString& request_id, const services::EconomicsResult& result) {
    // [FREE-MODE] Handle results from free_macro_aggregator.py
    if (result.source_id != kFinceptMacroSourceId)
        return;
    
    fetch_btn_->setEnabled(true);
    
    if (!result.success) {
        show_error(result.error);
        return;
    }
    
    // Display the macro data
    display_macro_data(result.data);
}

// ── i18n ──────────────────────────────────────────────────────────────────────

void FinceptMacroPanel::changeEvent(QEvent* event) {
    if (event->type() == QEvent::LanguageChange)
        retranslateUi();
    EconPanelBase::changeEvent(event);
}

void FinceptMacroPanel::retranslateUi() {
    if (coming_soon_lbl_)
        coming_soon_lbl_->setText(tr("FINCEPT MACRO — COMING SOON"));
    EconPanelBase::retranslateUi();
}

} // namespace fincept::screens