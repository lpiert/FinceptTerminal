#include "screens/polymarket/PolymarketStatusBar.h"

#include "ui/theme/Theme.h"

#include <QHBoxLayout>

namespace fincept::screens::polymarket {

using namespace fincept::ui;

PolymarketStatusBar::PolymarketStatusBar(QWidget* parent) : QWidget(parent) {
    setFixedHeight(22);
    setStyleSheet(QString("background: %1; border-top: 1px solid %2;").arg(colors::BG_RAISED(), colors::BORDER_DIM()));

    auto* hl = new QHBoxLayout(this);
    hl->setContentsMargins(16, 0, 16, 0);
    hl->setSpacing(12);

    auto label_style = QString("color: %1; font-size: 9px; background: transparent;").arg(colors::TEXT_SECONDARY());
    auto highlight_style = QString("color: %1; font-size: 9px; background: transparent;").arg(colors::CYAN());

    auto* brand = new QLabel("POLYMARKET");
    brand->setStyleSheet(label_style);
    hl->addWidget(brand);
    hl->addStretch(1);

    view_label_ = new QLabel("MARKETS");
    view_label_->setStyleSheet(label_style);
    hl->addWidget(view_label_);

    count_label_ = new QLabel;
    count_label_->setStyleSheet(label_style);
    hl->addWidget(count_label_);

    selected_label_ = new QLabel;
    selected_label_->setStyleSheet(highlight_style);
    hl->addWidget(selected_label_);

    ws_label_ = new QLabel;
    ws_label_->setStyleSheet(label_style);
    hl->addWidget(ws_label_);
    set_ws_status(false);
}

void PolymarketStatusBar::set_view(const QString& view) {
    view_label_->setText(view);
}

void PolymarketStatusBar::set_count(int count, const QString& label) {
    count_label_->setText(QString::number(count) + " " + label);
}

void PolymarketStatusBar::set_selected(const QString& question) {
    QString q = question.left(50);
    if (question.size() > 50)
        q += "...";
    selected_label_->setText(q);
}

void PolymarketStatusBar::set_ws_status(bool connected) {
    ws_connected_ = connected;
    if (connected) {
        ws_label_->setText(tr("鈼?LIVE"));
        ws_label_->setStyleSheet(
            QString("color: %1; font-size: 9px; font-weight: 700; background: transparent;").arg(colors::POSITIVE()));
    } else {
        ws_label_->setText(tr("鈼?OFF"));
        ws_label_->setStyleSheet(
            QString("color: %1; font-size: 8px; background: transparent;").arg(colors::TEXT_DIM()));
    }
}

void PolymarketStatusBar::set_brand(const QString& name, const QColor& accent) {
    accent_ = accent;
    brand_label_->setText(name.toUpper());
    brand_label_->setStyleSheet(
        QString("color: %1; font-size: 8px; font-weight: 700; letter-spacing: 1.5px; "
                "background: transparent;")
            .arg(accent_.name()));
    selected_label_->setStyleSheet(
        QString("color: %1; font-size: 8px; background: transparent;").arg(accent_.name()));
}

void PolymarketStatusBar::set_exchange_status(const QString& status) {
    if (status.isEmpty()) {
        exchange_status_->setVisible(false);
        return;
    }
    const QString upper = status.toUpper();
    QString color = colors::POSITIVE();
    if (upper == QStringLiteral("PAUSED") || upper == QStringLiteral("MAINT"))
        color = colors::AMBER();
    else if (upper == QStringLiteral("CLOSED") || upper == QStringLiteral("OFF"))
        color = colors::NEGATIVE();

    exchange_status_->setText(upper);
    exchange_status_->setStyleSheet(
        QString("color: %1; font-size: 8px; font-weight: 700; background: transparent;"
                "padding: 0 4px; border: 1px solid %1;")
            .arg(color));
    exchange_status_->setVisible(true);
}

void PolymarketStatusBar::set_next_session(const QString& text) {
    if (text.isEmpty()) {
        next_session_->setVisible(false);
        return;
    }
    next_session_->setText(text);
    next_session_->setVisible(true);
}

void PolymarketStatusBar::changeEvent(QEvent* event) {
    if (event->type() == QEvent::LanguageChange)
        retranslateUi();
    QWidget::changeEvent(event);
}

void PolymarketStatusBar::retranslateUi() {
    // Only the WS badge carries fixed UI text; brand / view / count / selected
    // / exchange-status all reflect caller-supplied data and refresh on update.
    set_ws_status(ws_connected_);
}

} // namespace fincept::screens::polymarket
