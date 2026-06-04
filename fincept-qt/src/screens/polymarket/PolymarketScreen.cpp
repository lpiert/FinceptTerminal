#include "screens/polymarket/PolymarketScreen.h"

#include "core/logging/Logger.h"
#include "core/session/ScreenStateManager.h"
#include "screens/polymarket/PolymarketBrowsePanel.h"
#include "screens/polymarket/PolymarketCommandBar.h"
#include "screens/polymarket/PolymarketDetailPanel.h"
#include "screens/polymarket/PolymarketLeaderboard.h"
#include "screens/polymarket/PolymarketStatusBar.h"
#include "services/polymarket/PolymarketService.h"
#include "services/polymarket/PolymarketWebSocket.h"
#include "ui/theme/Theme.h"

#include <QSplitter>
#include <QVBoxLayout>

namespace fincept::screens {

using namespace fincept::services::polymarket;
using namespace fincept::screens::polymarket;

// 鈹€鈹€ Constructor / Destructor 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

PolymarketScreen::PolymarketScreen(QWidget* parent) : QWidget(parent) {
    setObjectName("polyScreen");
    setStyleSheet(QString("background: %1;").arg(ui::colors::BG_BASE()));
    build_ui();
    connect_service();
    connect_websocket();

    refresh_timer_ = new QTimer(this);
    refresh_timer_->setInterval(60000);
    connect(refresh_timer_, &QTimer::timeout, this, &PolymarketScreen::on_refresh);

    LOG_INFO("Polymarket", "Screen constructed");
}

PolymarketScreen::~PolymarketScreen() {
    unsubscribe_current();
}

// 鈹€鈹€ Visibility (P3) 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

void PolymarketScreen::showEvent(QShowEvent* e) {
    QWidget::showEvent(e);
    refresh_timer_->start();
    if (first_show_) {
        first_show_ = false;
        PolymarketService::instance().fetch_tags();
        load_current_view();
    }
    if (has_selection_ && !subscribed_tokens_.isEmpty()) {
        PolymarketWebSocket::instance().subscribe(subscribed_tokens_);
    }
}

void PolymarketScreen::hideEvent(QHideEvent* e) {
    QWidget::hideEvent(e);
    refresh_timer_->stop();
}

// 鈹€鈹€ UI Build 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

void PolymarketScreen::build_ui() {
    auto* root = new QVBoxLayout(this);
    root->setContentsMargins(0, 0, 0, 0);
    root->setSpacing(0);

    command_bar_ = new PolymarketCommandBar;
    root->addWidget(command_bar_);

    auto* splitter = new QSplitter(Qt::Horizontal);
    splitter->setHandleWidth(1);
    splitter->setStyleSheet(QString("QSplitter::handle { background: %1; }").arg(ui::colors::BORDER_DIM()));

    browse_panel_ = new PolymarketBrowsePanel;
    browse_panel_->setMinimumWidth(320);
    browse_panel_->setMaximumWidth(420);

    detail_panel_ = new PolymarketDetailPanel;

    leaderboard_ = new PolymarketLeaderboard;
    leaderboard_->setMinimumWidth(280);
    leaderboard_->setMaximumWidth(340);
    leaderboard_->setVisible(false); // shown only in LEADERBOARD view (future)

    splitter->addWidget(browse_panel_);
    splitter->addWidget(detail_panel_);
    splitter->addWidget(leaderboard_);
    splitter->setStretchFactor(0, 0);
    splitter->setStretchFactor(1, 1);
    splitter->setStretchFactor(2, 0);
    splitter->setSizes({360, 700, 0});

    root->addWidget(splitter, 1);

    status_bar_ = new PolymarketStatusBar;
    root->addWidget(status_bar_);

    // Wire command bar signals
    connect(command_bar_, &PolymarketCommandBar::view_changed, this, &PolymarketScreen::on_view_changed);
    connect(command_bar_, &PolymarketCommandBar::category_changed, this, &PolymarketScreen::on_category_changed);
    connect(command_bar_, &PolymarketCommandBar::search_submitted, this, &PolymarketScreen::on_search_submitted);
    connect(command_bar_, &PolymarketCommandBar::sort_changed, this, &PolymarketScreen::on_sort_changed);
    connect(command_bar_, &PolymarketCommandBar::refresh_clicked, this, &PolymarketScreen::on_refresh);

    // Wire browse panel signals
    connect(browse_panel_, &PolymarketBrowsePanel::market_selected, this, &PolymarketScreen::on_market_selected);
    connect(browse_panel_, &PolymarketBrowsePanel::event_selected, this, &PolymarketScreen::on_event_selected);

    // Wire detail panel signals
    connect(detail_panel_, &PolymarketDetailPanel::interval_changed, this, &PolymarketScreen::on_interval_changed);
    connect(detail_panel_, &PolymarketDetailPanel::outcome_changed, this, &PolymarketScreen::on_outcome_changed);
    connect(detail_panel_, &PolymarketDetailPanel::related_market_clicked, this,
            &PolymarketScreen::on_related_market_clicked);
}

// 鈹€鈹€ Service Wiring 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

void PolymarketScreen::connect_service() {
    auto& svc = PolymarketService::instance();
    connect(&svc, &PolymarketService::markets_ready, this, &PolymarketScreen::on_markets_received);
    connect(&svc, &PolymarketService::events_ready, this, &PolymarketScreen::on_events_received);
    connect(&svc, &PolymarketService::tags_ready, this, &PolymarketScreen::on_tags_received);
    connect(&svc, &PolymarketService::order_book_ready, this, &PolymarketScreen::on_order_book_received);
    connect(&svc, &PolymarketService::price_history_ready, this, &PolymarketScreen::on_price_history_received);
    connect(&svc, &PolymarketService::trades_ready, this, &PolymarketScreen::on_trades_received);
    connect(&svc, &PolymarketService::price_summary_ready, this, &PolymarketScreen::on_price_summary_received);
    connect(&svc, &PolymarketService::top_holders_ready, this, &PolymarketScreen::on_top_holders_received);
    connect(&svc, &PolymarketService::leaderboard_ready, this, &PolymarketScreen::on_leaderboard_received);
    connect(&svc, &PolymarketService::comments_ready, this, &PolymarketScreen::on_comments_received);
    connect(&svc, &PolymarketService::related_markets_ready, this, &PolymarketScreen::on_related_markets_received);
    connect(&svc, &PolymarketService::request_error, this, &PolymarketScreen::on_service_error);
}

void PolymarketScreen::connect_websocket() {
    auto& ws = PolymarketWebSocket::instance();
    connect(&ws, &PolymarketWebSocket::price_updated, this, &PolymarketScreen::on_ws_price_updated);
    connect(&ws, &PolymarketWebSocket::orderbook_updated, this, &PolymarketScreen::on_ws_orderbook_updated);
    connect(&ws, &PolymarketWebSocket::connection_status_changed, this, &PolymarketScreen::on_ws_status_changed);
}

// 鈹€鈹€ Command Bar Slots 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

void PolymarketScreen::on_view_changed(const QString& view) {
    active_view_ = view;
    command_bar_->set_active_view(view);
    status_bar_->set_view(view);
    load_current_view();
    LOG_INFO("Polymarket", "View: " + view);
}

void PolymarketScreen::on_category_changed(const QString& category) {
    active_category_ = category;
    command_bar_->set_active_category(category);
    ScreenStateManager::instance().notify_changed(this);
    load_current_view();
}

void PolymarketScreen::on_search_submitted(const QString& query) {
    if (query.isEmpty()) {
        load_current_view();
        return;
    }
    command_bar_->set_loading(true);
    browse_panel_->set_loading(true);
    ++request_generation_;
    PolymarketService::instance().search_markets(query, 50);
}

void PolymarketScreen::on_sort_changed(const QString& sort_by) {
    active_sort_ = sort_by;
    if (!first_show_)
        load_current_view();
}

void PolymarketScreen::on_refresh() {
    load_current_view();
}

// 鈹€鈹€ Browse Panel Slots 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

void PolymarketScreen::on_market_selected(const Market& market) {
    select_market(market);
}

void PolymarketScreen::on_event_selected(const Event& event) {
    if (!event.markets.isEmpty()) {
        select_market(event.markets[0]);
    }
    // Also fetch related markets from this event
    if (event.id > 0) {
        PolymarketService::instance().fetch_related_markets(event.id);
    }
}

// 鈹€鈹€ Detail Panel Slots 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

void PolymarketScreen::on_interval_changed(const QString& interval) {
    if (!has_selection_ || selected_market_.clob_token_ids.isEmpty())
        return;
    int fidelity = 5;
    if (interval == "1h" || interval == "6h")
        fidelity = 1;
    else if (interval == "1w")
        fidelity = 30;
    else if (interval == "1m" || interval == "max")
        fidelity = 60;

    PolymarketService::instance().fetch_price_history(selected_market_.clob_token_ids[0], interval, fidelity);
}

void PolymarketScreen::on_outcome_changed(int index) {
    if (!has_selection_ || index < 0 || index >= selected_market_.clob_token_ids.size())
        return;
    PolymarketService::instance().fetch_price_history(selected_market_.clob_token_ids[index], "1d", 5);
}

void PolymarketScreen::on_related_market_clicked(const Market& market) {
    select_market(market);
}

// 鈹€鈹€ Data Loading 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

void PolymarketScreen::load_current_view() {
    command_bar_->set_loading(true);
    browse_panel_->set_loading(true);
    ++request_generation_;

    auto& svc = PolymarketService::instance();

    if (active_view_ == "TRENDING") {
        svc.fetch_markets("volume", 100, 0, false);
    } else if (active_view_ == "MARKETS") {
        if (active_category_ != "ALL") {
            svc.fetch_markets_by_tag(active_category_, active_sort_, 100, 0);
        } else {
            svc.fetch_markets(active_sort_, 100, 0, false);
        }
    } else if (active_view_ == "EVENTS") {
        svc.fetch_events(active_sort_, 100, 0, false);
    } else if (active_view_ == "SPORTS") {
        svc.fetch_markets_by_tag("sports", active_sort_, 100, 0);
    } else if (active_view_ == "RESOLVED") {
        svc.fetch_events("endDate", 100, 0, true);
    }
}

void PolymarketScreen::select_market(const Market& market) {
    unsubscribe_current();

    selected_market_ = market;
    has_selection_ = true;

    detail_panel_->set_market(market);
    status_bar_->set_selected(market.question);

    auto& svc = PolymarketService::instance();

    if (!market.clob_token_ids.isEmpty()) {
        QString token = market.clob_token_ids[0];
        svc.fetch_order_book(token);
        svc.fetch_price_summary(token);
        svc.fetch_price_history(token, "1d", 5);
    }
    if (!market.condition_id.isEmpty()) {
        svc.fetch_trades(market.condition_id, 100);
        svc.fetch_top_holders(market.condition_id, 20);
        svc.fetch_open_interest({market.condition_id});
    }
    if (!market.slug.isEmpty()) {
        svc.fetch_comments(market.slug, 50);
    }
    if (market.event_id > 0) {
        svc.fetch_related_markets(market.event_id);
    }

    subscribe_to_market(market);
}

void PolymarketScreen::subscribe_to_market(const Market& market) {
    subscribed_tokens_ = market.clob_token_ids;
    if (!subscribed_tokens_.isEmpty()) {
        PolymarketWebSocket::instance().subscribe(subscribed_tokens_);
    }
}

void PolymarketScreen::unsubscribe_current() {
    if (subscribed_asset_ids_.isEmpty()) return;
    if (auto* a = active_adapter())
        a->unsubscribe_market(subscribed_asset_ids_);
    subscribed_asset_ids_.clear();
}

// 鈹€鈹€ Adapter response handlers 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

void PolymarketScreen::on_markets_ready(const QVector<pred::PredictionMarket>& markets) {
    command_bar_->set_loading(false);
    browse_panel_->set_loading(false);
    browse_panel_->set_markets(markets);
    command_bar_->set_market_count(markets.size());
    status_bar_->set_count(markets.size(), tr("markets"));

    // Kalshi-only: fire a single /markets/candlesticks call covering all
    // visible tickers. The server returns ~7 daily points per ticker in
    // one round-trip, which populates sparklines without N per-card fetches.
    // Replaces the prior per-row candle-fetch fan-out (~20 HTTP calls per
    // page load in testing).
    if (auto* ks = dynamic_cast<pred::kalshi_ns::KalshiAdapter*>(active_adapter())) {
        QStringList tickers;
        tickers.reserve(markets.size());
        for (const auto& m : markets) {
            const QString& t = m.key.market_id;
            if (!t.isEmpty() && !batch_candles_cache_.contains(t)) tickers.push_back(t);
            if (tickers.size() >= 50) break;  // server caps batch at ~100
        }
        if (!tickers.isEmpty()) {
            const qint64 end = QDateTime::currentSecsSinceEpoch();
            const qint64 start = end - (7 * 24 * 3600);
            ks->fetch_batch_candles(tickers, /*period=*/1440, start, end);
        }
    }
}

// 鈹€鈹€ Service Response Handlers 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

void PolymarketScreen::on_markets_received(const QVector<Market>& markets) {
    command_bar_->set_loading(false);
    browse_panel_->set_markets(markets);
    command_bar_->set_market_count(markets.size());
    status_bar_->set_count(markets.size(), "markets");
}

void PolymarketScreen::on_events_received(const QVector<Event>& events) {
    command_bar_->set_loading(false);
    browse_panel_->set_events(events);
    command_bar_->set_market_count(events.size());
    status_bar_->set_count(events.size(), tr("events"));
}

void PolymarketScreen::on_search_results_ready(const QVector<pred::PredictionMarket>& markets,
                                               const QVector<pred::PredictionEvent>& events) {
    command_bar_->set_loading(false);
    browse_panel_->set_loading(false);
    if (!markets.isEmpty()) {
        browse_panel_->set_markets(markets);
        command_bar_->set_market_count(markets.size());
        status_bar_->set_count(markets.size(), tr("markets"));
    } else if (!events.isEmpty()) {
        browse_panel_->set_events(events);
        command_bar_->set_market_count(events.size());
        status_bar_->set_count(events.size(), tr("events"));
    } else {
        command_bar_->set_market_count(0);
        status_bar_->set_count(0, tr("results"));
    }
}

void PolymarketScreen::on_tags_ready(const QStringList& tags) {
    command_bar_->set_categories(tags);
}

void PolymarketScreen::on_order_book_received(const OrderBook& book) {
    detail_panel_->set_order_book(book);
}

void PolymarketScreen::on_price_history_received(const PriceHistory& history) {
    detail_panel_->set_price_history(history);
}

void PolymarketScreen::on_trades_received(const QVector<Trade>& trades) {
    detail_panel_->set_trades(trades);
}

void PolymarketScreen::on_price_summary_received(const PriceSummary& summary) {
    detail_panel_->set_price_summary(summary);
}

void PolymarketScreen::on_top_holders_received(const QVector<TopHolder>& holders) {
    detail_panel_->set_top_holders(holders);
}

void PolymarketScreen::on_leaderboard_received(const QVector<LeaderboardEntry>& entries) {
    leaderboard_->set_entries(entries);
}

void PolymarketScreen::on_comments_received(const QVector<Comment>& comments) {
    detail_panel_->set_comments(comments);
}

void PolymarketScreen::on_related_markets_received(const QVector<Market>& markets) {
    detail_panel_->set_related_markets(markets);
}

void PolymarketScreen::on_service_error(const QString& ctx, const QString& msg) {
    command_bar_->set_loading(false);
    LOG_ERROR("Polymarket", ctx + ": " + msg);
}

// 鈹€鈹€ WebSocket Handlers 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

void PolymarketScreen::on_ws_price_updated(const QString& asset_id, double price) {
    // Update detail panel if this is our selected market
    if (has_selection_) {
        for (int i = 0; i < selected_market_.clob_token_ids.size(); ++i) {
            if (selected_market_.clob_token_ids[i] == asset_id) {
                if (i < selected_market_.outcomes.size()) {
                    selected_market_.outcomes[i].price = price;
                    detail_panel_->set_market(selected_market_);
                }
                break;
            }
        }
    }
}

void PolymarketScreen::on_ws_orderbook_updated(const QString& /*asset_id*/, const OrderBook& book) {
    detail_panel_->set_order_book(book);
}

void PolymarketScreen::on_ws_status_changed(bool connected) {
    command_bar_->set_ws_status(connected);
    status_bar_->set_ws_status(connected);
}

// 鈹€鈹€ Polymarket-only enrichment handlers 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

void PolymarketScreen::on_price_summary_received(const pmx::PriceSummary& summary) {
    if (!active_is_polymarket() || !detail_panel_) return;
    detail_panel_->set_price_summary(summary);
}

void PolymarketScreen::on_top_holders_received(const QVector<pmx::TopHolder>& holders) {
    if (!active_is_polymarket() || !detail_panel_) return;
    detail_panel_->set_top_holders(holders);
}

void PolymarketScreen::on_comments_received(const QVector<pmx::Comment>& comments) {
    if (!active_is_polymarket() || !detail_panel_) return;
    detail_panel_->set_comments(comments);
}

void PolymarketScreen::on_related_markets_received(const QVector<pmx::Market>& markets) {
    if (!active_is_polymarket() || !detail_panel_) return;
    // Legacy polymarket::Market 鈫?prediction::PredictionMarket shim. The
    // detail panel only cares about question + volume for the related-market
    // cards, so we fill in the minimum.
    QVector<pred::PredictionMarket> out;
    out.reserve(markets.size());
    for (const auto& m : markets) {
        pred::PredictionMarket pm;
        pm.key.exchange_id = kPolymarketId();
        pm.key.market_id = m.condition_id;
        pm.question = m.question;
        pm.volume = m.volume;
        pm.liquidity = m.liquidity;
        pm.active = m.active;
        pm.closed = m.closed;
        for (const auto& o : m.outcomes) {
            pred::Outcome po;
            po.name = o.name;
            po.price = o.price;
            pm.outcomes.push_back(po);
        }
        // Map clob_token_ids into outcomes so the user can click through
        // and drive select_market() with a full asset_id list.
        for (int i = 0; i < m.clob_token_ids.size() && i < pm.outcomes.size(); ++i)
            pm.outcomes[i].asset_id = m.clob_token_ids[i];
        pm.extras["slug"] = m.slug;
        pm.key.event_id = QString::number(m.event_id);
        out.push_back(pm);
    }
    detail_panel_->set_related_markets(out);
}

// 鈹€鈹€ Kalshi-specific handlers 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

void PolymarketScreen::on_kalshi_exchange_status(const QJsonObject& status) {
    if (!status_bar_) return;
    // Kalshi responds with { "exchange_active": bool, "trading_active": bool,
    // "exchange_estopped": bool } on /exchange/status. We map this to a
    // user-facing label: PAUSED if estopped, OPEN if both booleans true,
    // CLOSED otherwise.
    const bool exchange_active = status.value("exchange_active").toBool();
    const bool trading_active = status.value("trading_active").toBool();
    const bool estopped = status.value("exchange_estopped").toBool();
    QString label;
    if (estopped) label = QStringLiteral("PAUSED");
    else if (exchange_active && trading_active) label = QStringLiteral("OPEN");
    else if (exchange_active) label = QStringLiteral("MAINT");
    else label = QStringLiteral("CLOSED");
    status_bar_->set_exchange_status(label);
}

void PolymarketScreen::on_kalshi_exchange_schedule(const QJsonObject& schedule) {
    if (!status_bar_) return;
    // Best-effort "next open" label. Kalshi's schedule shape is nested
    // (standard_hours + maintenance_windows). Fall back to an empty string
    // if the shape changes so we don't surface nonsense.
    const auto standard = schedule.value("schedule").toObject()
                              .value("standard_hours").toArray();
    QString next;
    if (!standard.isEmpty()) {
        const auto first = standard.first().toObject();
        const QString open = first.value("open_time").toString();
        if (!open.isEmpty())
            next = tr("Next open: ") + open;
    }
    status_bar_->set_next_session(next);
}

void PolymarketScreen::on_kalshi_ws_trade(const pred::PredictionTrade& trade) {
    if (!detail_panel_ || !has_selection_) return;
    // Only surface trades for the currently-selected market. Kalshi's trade
    // channel broadcasts across all subscribed tickers, so we filter here.
    const QString aid_prefix = selected_market_.key.market_id + QStringLiteral(":");
    if (!trade.asset_id.startsWith(aid_prefix)) return;
    if (auto* feed = detail_panel_->findChild<polymarket::PolymarketActivityFeed*>())
        feed->append_trade(trade);
}

void PolymarketScreen::on_kalshi_market_lifecycle(const QString& ticker,
                                                  const QString& status) {
    LOG_INFO("PredictionMarkets",
             QStringLiteral("Kalshi lifecycle: %1 鈫?%2").arg(ticker, status));
    // When a visible market flips status, refresh just that row. Avoid
    // reloading the whole view 鈥?a market going paused/closed shouldn't
    // disturb the rest of the browse panel.
    if (!active_adapter()) return;
    // If the currently-selected market just flipped, refresh detail too.
    if (has_selection_ && selected_market_.key.market_id == ticker) {
        pred::MarketKey k;
        k.market_id = ticker;
        active_adapter()->fetch_market(k);
    }
}

void PolymarketScreen::on_kalshi_batch_candles(
    const QHash<QString, pred::PriceHistory>& histories) {
    // Store for sparkline consumers (browse panel cards). The browse panel
    // will re-read from the cache on its next rebuild.
    for (auto it = histories.constBegin(); it != histories.constEnd(); ++it)
        batch_candles_cache_.insert(it.key(), it.value());
    // If the browse panel exposes a set_sparklines() hook, wire it here.
    // Without a hook it's still useful for the detail chart which checks
    // the cache before issuing its own fetch.
}

void PolymarketScreen::on_kalshi_market_detail(const pred::PredictionMarket& market) {
    // Single-row refresh triggered by a lifecycle event. Update the browse
    // panel row in place if possible; otherwise no-op (panel won't show
    // stale data because the full-view refresh will replace it soon).
    if (browse_panel_) browse_panel_->update_market_row(market);
    if (has_selection_ && selected_market_.key.market_id == market.key.market_id) {
        selected_market_ = market;
        if (detail_panel_) detail_panel_->set_market(market);
    }
}

void PolymarketScreen::on_open_orders_ready(const QVector<pred::OpenOrder>& orders) {
    if (order_blotter_) order_blotter_->set_orders(orders);
}

void PolymarketScreen::on_order_refresh_requested(const QString& order_id) {
    // Only Kalshi supports the single-order fetch today. Polymarket has no
    // REST equivalent 鈥?the blotter's refresh button is wired for everyone
    // but the cast below makes the no-op explicit on other adapters.
    auto* a = active_adapter();
    if (auto* ks = dynamic_cast<pred::kalshi_ns::KalshiAdapter*>(a)) {
        ks->fetch_order(order_id);
    } else if (a) {
        a->fetch_open_orders();  // fall back to refetching the whole list
    }
}

void PolymarketScreen::on_order_amend_requested(const QString& order_id, const QString& side,
                                                double price) {
    auto* a = active_adapter();
    auto* ks = dynamic_cast<pred::kalshi_ns::KalshiAdapter*>(a);
    if (!ks) {
        LOG_WARN("PredictionMarkets", "Amend not supported on this adapter");
        return;
    }
    // Kalshi accepts integer cents 1-99.
    const int cents = qBound(1, int(std::round(price * 100.0)), 99);
    ks->amend_order(order_id, side, cents);
}

void PolymarketScreen::on_order_cancel_requested(const QString& order_id) {
    if (auto* a = active_adapter()) a->cancel_order(order_id);
}

void PolymarketScreen::on_orders_cancel_all_requested(const QStringList& order_ids) {
    auto* a = active_adapter();
    if (!a) return;
    // Prefer the batched endpoint when the adapter supports it (Kalshi);
    // otherwise fall back to N individual cancels so Polymarket users still
    // get the Cancel All action.
    if (auto* ks = dynamic_cast<pred::kalshi_ns::KalshiAdapter*>(a)) {
        ks->cancel_orders_batch(order_ids);
    } else {
        for (const auto& oid : order_ids) a->cancel_order(oid);
    }
}

void PolymarketScreen::on_kalshi_single_order(const QJsonObject& order) {
    if (!order_blotter_) return;
    // Translate the raw Kalshi order JSON into the unified OpenOrder shape
    // the blotter expects. Field names match the Python bridge's
    // cmd_open_orders normalization so the two paths produce identical
    // rows.
    pred::OpenOrder o;
    o.order_id = order.value("order_id").toString();
    const QString side = order.value("side").toString().toLower();
    o.outcome = side.toUpper();
    o.asset_id = order.value("ticker").toString() + ":" + side;
    o.market_id = order.value("ticker").toString();
    o.side = order.value("action").toString().toUpper();
    o.order_type = order.value("type").toString().toUpper();
    const QString price_key = (side == "yes") ? "yes_price_dollars" : "no_price_dollars";
    o.price = order.value(price_key).toString().toDouble();
    o.size = order.value("remaining_count_fp").toString().toDouble();
    const double initial = order.value("initial_count_fp").toString().toDouble();
    o.filled = qMax(0.0, initial - o.size);
    o.status = order.value("status").toString().toUpper();
    order_blotter_->update_order(o);
}

void PolymarketScreen::on_kalshi_series_detail(const QString& series_ticker,
                                               const QJsonObject& series) {
    if (!detail_panel_ || !has_selection_) return;
    // Only apply if the currently-selected market is in this series.
    const QString selected_series =
        selected_market_.extras.value(QStringLiteral("series_ticker")).toString();
    if (series_ticker != selected_series) return;

    const QString title = series.value(QStringLiteral("title")).toString();
    const QString frequency = series.value(QStringLiteral("frequency")).toString();
    const QString fee_type = series.value(QStringLiteral("fee_type")).toString();
    const double fee_mult = series.value(QStringLiteral("fee_multiplier")).toDouble();
    const QString contract_url = series.value(QStringLiteral("contract_url")).toString();

    QStringList lines;
    if (!title.isEmpty()) lines << QStringLiteral("<b>%1</b>").arg(title.toHtmlEscaped());
    if (!series_ticker.isEmpty())
        lines << tr("Series: %1").arg(series_ticker);
    if (!frequency.isEmpty())
        lines << tr("Frequency: %1").arg(frequency);
    if (!fee_type.isEmpty()) {
        QString fee_line = tr("Fees: %1").arg(fee_type);
        if (fee_mult > 0.0)
            fee_line += QStringLiteral(" (脳%1)").arg(fee_mult);
        lines << fee_line;
    }
    if (!contract_url.isEmpty())
        lines << QStringLiteral("<i>%1</i>").arg(contract_url.toHtmlEscaped());

    detail_panel_->set_series_tooltip(lines.join(QStringLiteral("<br>")));
}

// 鈹€鈹€ IStatefulScreen 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

QVariantMap PolymarketScreen::save_state() const {
    QVariantMap state{
        {"category", active_category_},
        {"view", active_view_},
        {"sort", active_sort_},
    };
    if (command_bar_) state["search"] = command_bar_->search_text();
    return state;
}

void PolymarketScreen::restore_state(const QVariantMap& state) {
    const QString cat = state.value("category", "ALL").toString();
    const QString view = state.value("view", "MARKETS").toString();
    const QString sort = state.value("sort", "volume").toString();

    active_sort_ = sort;
    active_view_ = view;
    on_category_changed(cat);
    if (command_bar_ && state.contains("search"))
        command_bar_->set_search_text(state.value("search").toString());
}

} // namespace fincept::screens
