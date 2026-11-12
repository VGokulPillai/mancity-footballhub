"""Man City Ticketing Intelligence Platform — Databricks App.

A bespoke ticketing analytics application built on AI-ready pipelines,
featuring revenue analytics, seat intelligence, fan segmentation,
pricing distribution, and pipeline health monitoring.
"""

import os, datetime
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px

from backend import get_backend

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True,
    title="Ticketing Intelligence",
)
server = app.server

# ── Palette ──
BG = "#0b1120"
PANEL = "#111827"
CARD = "#1a2234"
ACCENT = "#6CADDF"
GREEN = "#34d399"
AMBER = "#fbbf24"
RED = "#f87171"
WHITE = "#f1f5f9"
MUTED = "#64748b"
BORDER = "#1e293b"

backend = get_backend()
SEASONS = ["25/26", "24/25", "23/24"]


# ── SVG Icons ──
def _svg(path_d, size=20, color=ACCENT):
    return html.Iframe(
        srcDoc=f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" fill="{color}" viewBox="0 0 24 24"><path d="{path_d}"/></svg>',
        style={"width": f"{size}px", "height": f"{size}px", "border": "none", "overflow": "hidden", "verticalAlign": "middle"},
    )

ICO_TICKET = "M22 10V6a2 2 0 00-2-2H4a2 2 0 00-2 2v4a2 2 0 010 4v4a2 2 0 002 2h16a2 2 0 002-2v-4a2 2 0 010-4zm-2-1.46a4 4 0 000 6.92V18H4v-2.54a4 4 0 000-6.92V6h16v2.54z"
ICO_MONEY = "M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"
ICO_PEOPLE = "M16 11c1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3 1.34 3 3 3zm-8 0c1.66 0 3-1.34 3-3S9.66 5 8 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"
ICO_CHART = "M3.5 18.49l6-6.01 4 4L22 6.92l-1.41-1.41-7.09 7.97-4-4L2 16.99z"
ICO_SEAT = "M4 18v3h3v-3h10v3h3v-3h1a1 1 0 001-1v-5h-2V7a3 3 0 00-3-3H7a3 3 0 00-3 3v5H2v5a1 1 0 001 1h1zM6 7a1 1 0 011-1h10a1 1 0 011 1v5H6V7z"
ICO_AI = "M21 10.12h-6.78l2.74-2.82-2.2-2.2L12 7.94V1.16h-3.12V7.94L6.22 5.1 4.04 7.3l2.74 2.82H0v3.12h6.78l-2.74 2.82 2.18 2.2L9 15.22v6.78h3.12v-6.78l2.66 2.84 2.2-2.2-2.74-2.82H21z"
ICO_PIPE = "M19.35 10.04A7.49 7.49 0 0012 4C9.11 4 6.6 5.64 5.35 8.04A5.994 5.994 0 000 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z"


def _kpi(title, value, icon_d, prefix="", suffix="", delta=None, delta_good=True):
    if isinstance(value, float) and value == int(value):
        value = int(value)
    if isinstance(value, (int, float)):
        if abs(value) >= 1_000_000:
            txt = f"{prefix}£{value/1_000_000:.1f}M" if prefix == "£" else f"{prefix}{value:,.0f}{suffix}"
        else:
            txt = f"{prefix}{value:,.0f}{suffix}" if isinstance(value, int) else f"{prefix}{value}{suffix}"
    else:
        txt = f"{prefix}{value}{suffix}"

    delta_el = None
    if delta is not None:
        clr = GREEN if delta_good else RED
        arrow = "▲" if delta >= 0 else "▼"
        delta_el = html.Span(f" {arrow}{abs(delta)}%", style={"color": clr, "fontSize": "0.7rem", "fontWeight": "600"})

    return dbc.Col(html.Div([
        html.Div([_svg(icon_d, 18)], style={"marginBottom": "4px"}),
        html.Div(title, style={"fontSize": "0.62rem", "color": MUTED, "textTransform": "uppercase", "letterSpacing": "1px", "fontWeight": "500"}),
        html.Div([
            html.Span(txt, style={"fontSize": "1.3rem", "fontWeight": "700", "color": WHITE}),
            delta_el or html.Span(),
        ]),
    ], style={"textAlign": "center", "padding": "14px 6px", "background": CARD, "borderRadius": "8px", "border": f"1px solid {BORDER}"}), width=True)


_CL = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
           font=dict(color=MUTED, size=10), margin=dict(l=40, r=12, t=8, b=32),
           xaxis=dict(gridcolor=BORDER, showgrid=False), yaxis=dict(gridcolor=BORDER, showgrid=False))


# ── Sidebar ──
def _nav(label, href, icon_d, active_path=None):
    active = active_path == href if active_path else False
    return html.A([
        _svg(icon_d, 16, ACCENT if active else MUTED),
        html.Span(label, style={"marginLeft": "8px"}),
    ], href=href, style={
        "display": "flex", "alignItems": "center", "padding": "9px 16px",
        "color": WHITE if active else MUTED, "fontSize": "0.8rem", "textDecoration": "none",
        "borderLeft": f"3px solid {ACCENT}" if active else "3px solid transparent",
        "background": f"rgba(108,173,223,0.06)" if active else "transparent",
        "fontWeight": "600" if active else "400",
    })


def sidebar():
    return html.Div([
        html.Div([
            html.Img(src="/assets/mancity-crest.png", style={"height": "42px"}),
            html.Div([
                html.Div("Ticketing Intelligence", style={"color": WHITE, "fontWeight": "700", "fontSize": "0.85rem", "lineHeight": "1.1"}),
                html.Div("Platform", style={"color": ACCENT, "fontWeight": "600", "fontSize": "0.7rem"}),
            ], style={"marginLeft": "8px"}),
        ], style={"display": "flex", "alignItems": "center", "padding": "16px", "borderBottom": f"1px solid {BORDER}"}),

        html.Div([
            html.Div("ANALYTICS", style={"color": MUTED, "fontSize": "0.6rem", "letterSpacing": "1.5px", "padding": "14px 16px 4px", "fontWeight": "600"}),
            _nav("Command Center", "/", ICO_CHART),
            _nav("Revenue Analytics", "/revenue", ICO_MONEY),
            _nav("Seat Intelligence", "/seats", ICO_SEAT),
            _nav("Fan Segments", "/fans", ICO_PEOPLE),
            _nav("Match Explorer", "/matches", ICO_TICKET),
            html.Div("OPERATIONS", style={"color": MUTED, "fontSize": "0.6rem", "letterSpacing": "1.5px", "padding": "18px 16px 4px", "fontWeight": "600"}),
            _nav("Pipeline Health", "/pipeline", ICO_PIPE),
            _nav("Support", "/support", ICO_AI),
        ], style={"flex": "1", "overflowY": "auto"}),

        html.Div([
            html.Div([
                html.Img(src="/assets/databricks-logo.png", style={"height": "16px", "opacity": "0.6"}),
                html.Span(" Powered by Databricks", style={"color": MUTED, "fontSize": "0.65rem", "marginLeft": "4px"}),
            ], style={"display": "flex", "alignItems": "center"}),
        ], style={"padding": "12px 16px", "borderTop": f"1px solid {BORDER}"}),
    ], style={
        "background": PANEL, "width": "210px", "minHeight": "100vh",
        "display": "flex", "flexDirection": "column",
        "position": "fixed", "left": 0, "top": 0, "zIndex": 1000,
        "borderRight": f"1px solid {BORDER}",
    })


def top_bar(title="Command Center"):
    return html.Div([
        html.Div([
            html.Span(title, style={"fontWeight": "700", "color": WHITE, "fontSize": "1rem"}),
            html.Span(f"Season 25/26", style={"color": MUTED, "fontSize": "0.75rem", "marginLeft": "14px",
                       "background": CARD, "padding": "2px 10px", "borderRadius": "10px"}),
        ]),
        html.Div([
            html.Span(f"Updated {datetime.date.today().strftime('%d %b %Y')}", style={"color": MUTED, "fontSize": "0.72rem"}),
            dcc.Dropdown(id="season-select", options=[{"label": s, "value": s} for s in SEASONS],
                         value="25/26", clearable=False,
                         style={"width": "90px", "fontSize": "0.75rem", "display": "inline-block", "marginLeft": "10px"}),
        ], style={"display": "flex", "alignItems": "center", "gap": "8px"}),
    ], style={
        "display": "flex", "justifyContent": "space-between", "alignItems": "center",
        "padding": "10px 20px", "background": PANEL, "borderBottom": f"1px solid {BORDER}",
    })


# ═══════════════════════════════════════════
# PAGE: COMMAND CENTER (Home)
# ═══════════════════════════════════════════
def command_center():
    k = backend.get_ticketing_kpis()
    return html.Div([
        top_bar("Command Center"),
        html.Div([
            # KPI strip
            dbc.Row([
                _kpi("Revenue", k["total_revenue"], ICO_MONEY, prefix="£", delta=8.2),
                _kpi("Tickets Sold", k["tickets_sold"], ICO_TICKET, delta=3.1),
                _kpi("Unique Buyers", k["unique_buyers"], ICO_PEOPLE, delta=5.4),
                _kpi("Attendance", k["attendance_pct"], ICO_CHART, suffix="%"),
                _kpi("Avg Price", k["avg_ticket_price"], ICO_MONEY, prefix="£"),
                _kpi("Season Tickets", k["season_ticket_holders"], ICO_SEAT),
            ], className="g-2 mb-3"),

            # Row 2: Revenue trend + Competition split
            dbc.Row([
                dbc.Col([
                    html.Div("REVENUE TREND", style={"color": WHITE, "fontSize": "0.78rem", "fontWeight": "600", "marginBottom": "6px"}),
                    dcc.Graph(id="chart-rev-trend", config={"displayModeBar": False}, style={"height": "220px"}),
                ], md=8, style={"background": CARD, "borderRadius": "8px", "padding": "14px", "border": f"1px solid {BORDER}"}),
                dbc.Col([
                    html.Div("BY COMPETITION", style={"color": WHITE, "fontSize": "0.78rem", "fontWeight": "600", "marginBottom": "6px"}),
                    dcc.Graph(id="chart-comp-split", config={"displayModeBar": False}, style={"height": "220px"}),
                ], md=4, style={"background": CARD, "borderRadius": "8px", "padding": "14px", "border": f"1px solid {BORDER}"}),
            ], className="g-2 mb-3"),

            # Row 3: Sale Channels + Demographics + One-off gauge
            dbc.Row([
                dbc.Col([
                    html.Div("SALE CHANNELS", style={"color": WHITE, "fontSize": "0.78rem", "fontWeight": "600", "marginBottom": "6px"}),
                    dcc.Graph(id="chart-channels", config={"displayModeBar": False}, style={"height": "210px"}),
                ], md=4, style={"background": CARD, "borderRadius": "8px", "padding": "14px", "border": f"1px solid {BORDER}"}),
                dbc.Col([
                    html.Div("ATTENDERS — AGE", style={"color": WHITE, "fontSize": "0.78rem", "fontWeight": "600", "marginBottom": "6px"}),
                    dcc.Graph(id="chart-age", config={"displayModeBar": False}, style={"height": "210px"}),
                ], md=4, style={"background": CARD, "borderRadius": "8px", "padding": "14px", "border": f"1px solid {BORDER}"}),
                dbc.Col([
                    html.Div("ONE-OFF ATTENDERS", style={"color": WHITE, "fontSize": "0.78rem", "fontWeight": "600", "marginBottom": "6px"}),
                    dcc.Graph(id="chart-oneoff", config={"displayModeBar": False}, style={"height": "210px"}),
                ], md=4, style={"background": CARD, "borderRadius": "8px", "padding": "14px", "border": f"1px solid {BORDER}"}),
            ], className="g-2"),
        ], style={"padding": "16px 20px"}),
    ])


# ═══════════════════════════════════════════
# PAGE: REVENUE ANALYTICS
# ═══════════════════════════════════════════
def revenue_page():
    k = backend.get_ticketing_kpis()
    return html.Div([
        top_bar("Revenue Analytics"),
        html.Div([
            dbc.Row([
                _kpi("Total Revenue", k["total_revenue"], ICO_MONEY, prefix="£"),
                _kpi("Revenue / Match", k["revenue_per_match"], ICO_MONEY, prefix="£"),
                _kpi("Sell-Through", k["sell_through_pct"], ICO_CHART, suffix="%"),
                _kpi("Digital Sales", k["digital_sales_pct"], ICO_CHART, suffix="%"),
            ], className="g-2 mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Div("REVENUE BY MATCH", style={"color": WHITE, "fontSize": "0.78rem", "fontWeight": "600", "marginBottom": "6px"}),
                    dcc.Graph(id="chart-rev-match", config={"displayModeBar": False}, style={"height": "340px"}),
                ], md=8, style={"background": CARD, "borderRadius": "8px", "padding": "14px", "border": f"1px solid {BORDER}"}),
                dbc.Col([
                    html.Div("PRICE DISTRIBUTION", style={"color": WHITE, "fontSize": "0.78rem", "fontWeight": "600", "marginBottom": "6px"}),
                    dcc.Graph(id="chart-price-dist", config={"displayModeBar": False}, style={"height": "340px"}),
                ], md=4, style={"background": CARD, "borderRadius": "8px", "padding": "14px", "border": f"1px solid {BORDER}"}),
            ], className="g-2"),
        ], style={"padding": "16px 20px"}),
    ])


# ═══════════════════════════════════════════
# PAGE: SEAT INTELLIGENCE
# ═══════════════════════════════════════════
def seats_page():
    df = backend.get_section_occupancy()
    rows = [html.Tr([
        html.Td(r["section"], style={"color": WHITE, "fontSize": "0.8rem"}),
        html.Td(f'{int(r["capacity"]):,}', style={"color": MUTED}),
        html.Td(html.Div([
            html.Div(style={"width": f'{r["avg_occupancy_pct"]}%', "height": "6px", "background": GREEN if r["avg_occupancy_pct"] > 90 else (AMBER if r["avg_occupancy_pct"] > 80 else RED), "borderRadius": "3px"}),
            html.Span(f'{r["avg_occupancy_pct"]}%', style={"color": WHITE, "fontSize": "0.75rem", "marginLeft": "6px"}),
        ], style={"display": "flex", "alignItems": "center", "gap": "4px"})),
        html.Td(f'£{int(r["avg_revenue"]):,}', style={"color": ACCENT}),
        html.Td(f'{r["season_ticket_pct"]}%', style={"color": MUTED}),
    ]) for _, r in df.iterrows()]

    return html.Div([
        top_bar("Seat Intelligence"),
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div("SECTION OCCUPANCY", style={"color": WHITE, "fontSize": "0.78rem", "fontWeight": "600", "marginBottom": "6px"}),
                    dcc.Graph(id="chart-seat-heat", config={"displayModeBar": False}, style={"height": "300px"}),
                ], md=7, style={"background": CARD, "borderRadius": "8px", "padding": "14px", "border": f"1px solid {BORDER}"}),
                dbc.Col([
                    html.Div("OCCUPANCY DISTRIBUTION", style={"color": WHITE, "fontSize": "0.78rem", "fontWeight": "600", "marginBottom": "6px"}),
                    dcc.Graph(id="chart-seat-dist", config={"displayModeBar": False}, style={"height": "300px"}),
                ], md=5, style={"background": CARD, "borderRadius": "8px", "padding": "14px", "border": f"1px solid {BORDER}"}),
            ], className="g-2 mb-3"),
            html.Div([
                html.Div("SECTION DETAIL", style={"color": WHITE, "fontSize": "0.78rem", "fontWeight": "600", "marginBottom": "8px"}),
                dbc.Table([
                    html.Thead(html.Tr([html.Th("Section"), html.Th("Capacity"), html.Th("Occupancy"), html.Th("Revenue"), html.Th("Season %")])),
                    html.Tbody(rows),
                ], bordered=True, hover=True, striped=True, size="sm"),
            ], style={"background": CARD, "borderRadius": "8px", "padding": "14px", "border": f"1px solid {BORDER}"}),
        ], style={"padding": "16px 20px"}),
    ])


# ═══════════════════════════════════════════
# PAGE: FAN SEGMENTS
# ═══════════════════════════════════════════
def fans_page():
    return html.Div([
        top_bar("Fan Segments"),
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div("BUYER SEGMENTS", style={"color": WHITE, "fontSize": "0.78rem", "fontWeight": "600", "marginBottom": "6px"}),
                    dcc.Graph(id="chart-segments", config={"displayModeBar": False}, style={"height": "300px"}),
                ], md=6, style={"background": CARD, "borderRadius": "8px", "padding": "14px", "border": f"1px solid {BORDER}"}),
                dbc.Col([
                    html.Div("ATTENDERS — DISTANCE", style={"color": WHITE, "fontSize": "0.78rem", "fontWeight": "600", "marginBottom": "6px"}),
                    dcc.Graph(id="chart-distance", config={"displayModeBar": False}, style={"height": "300px"}),
                ], md=6, style={"background": CARD, "borderRadius": "8px", "padding": "14px", "border": f"1px solid {BORDER}"}),
            ], className="g-2 mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Div("ATTENDERS — GENDER", style={"color": WHITE, "fontSize": "0.78rem", "fontWeight": "600", "marginBottom": "6px"}),
                    dcc.Graph(id="chart-gender", config={"displayModeBar": False}, style={"height": "240px"}),
                ], md=4, style={"background": CARD, "borderRadius": "8px", "padding": "14px", "border": f"1px solid {BORDER}"}),
                dbc.Col([
                    html.Div("INTERNATIONAL FANS", style={"color": WHITE, "fontSize": "0.78rem", "fontWeight": "600", "marginBottom": "6px"}),
                    dcc.Graph(id="chart-countries", config={"displayModeBar": False}, style={"height": "240px"}),
                ], md=8, style={"background": CARD, "borderRadius": "8px", "padding": "14px", "border": f"1px solid {BORDER}"}),
            ], className="g-2"),
        ], style={"padding": "16px 20px"}),
    ])


# ═══════════════════════════════════════════
# PAGE: MATCH EXPLORER
# ═══════════════════════════════════════════
def matches_page():
    df = backend.get_revenue_by_match()
    rows = [html.Tr([
        html.Td(r["match"], style={"color": WHITE, "fontWeight": "600", "fontSize": "0.8rem"}),
        html.Td(r["date"], style={"color": MUTED, "fontSize": "0.78rem"}),
        html.Td(dbc.Badge(r["competition"], color="info" if r["competition"] == "PL" else ("warning" if r["competition"] == "UCL" else "secondary"), style={"fontSize": "0.65rem"})),
        html.Td(f'£{int(r["revenue"]):,}', style={"color": ACCENT, "fontWeight": "600"}),
        html.Td(f'{int(r["tickets_sold"]):,}', style={"color": WHITE}),
        html.Td(f'{int(r["attendance"]):,}', style={"color": WHITE}),
        html.Td(html.Div([
            html.Div(style={"width": f'{min(r["sell_through"], 100)}%', "height": "5px", "background": GREEN if r["sell_through"] > 90 else AMBER, "borderRadius": "3px"}),
        ], style={"width": "60px", "background": BORDER, "borderRadius": "3px", "display": "inline-block"})),
        html.Td(f'£{r["avg_price"]:.0f}', style={"color": MUTED}),
    ]) for _, r in df.iterrows()]

    return html.Div([
        top_bar("Match Explorer"),
        html.Div([
            html.Div([
                html.Div(f"{len(df)} MATCHES", style={"color": ACCENT, "fontSize": "0.7rem", "fontWeight": "600", "letterSpacing": "1px", "marginBottom": "8px"}),
                dbc.Table([
                    html.Thead(html.Tr([html.Th("Match"), html.Th("Date"), html.Th("Comp"), html.Th("Revenue"), html.Th("Sold"), html.Th("Attend."), html.Th("Sell %"), html.Th("Avg £")])),
                    html.Tbody(rows),
                ], bordered=True, hover=True, striped=True, size="sm"),
            ], style={"background": CARD, "borderRadius": "8px", "padding": "14px", "border": f"1px solid {BORDER}"}),
        ], style={"padding": "16px 20px"}),
    ])


# ═══════════════════════════════════════════
# PAGE: PIPELINE HEALTH
# ═══════════════════════════════════════════
def pipeline_page():
    health = backend.get_pipeline_health()
    rows = [html.Tr([
        html.Td(h["table"], style={"color": WHITE, "fontSize": "0.78rem", "fontFamily": "monospace"}),
        html.Td(h["rows"], style={"color": MUTED}),
        html.Td(h["last_updated"], style={"color": MUTED, "fontSize": "0.75rem"}),
        html.Td(dbc.Badge(h["freshness"], color="success" if h["freshness"] == "live" else "warning")),
        html.Td(html.Div([
            html.Div(style={"width": f'{h["quality_score"]}%', "height": "6px",
                             "background": GREEN if h["quality_score"] > 95 else (AMBER if h["quality_score"] > 90 else RED),
                             "borderRadius": "3px"}),
            html.Span(f'{h["quality_score"]}%', style={"fontSize": "0.7rem", "color": WHITE, "marginLeft": "4px"}),
        ], style={"display": "flex", "alignItems": "center"})),
    ]) for h in health]

    live = sum(1 for h in health if h["freshness"] == "live")
    avg_q = sum(h["quality_score"] for h in health) / len(health)

    return html.Div([
        top_bar("Pipeline Health"),
        html.Div([
            dbc.Row([
                _kpi("Tables Tracked", len(health), ICO_PIPE),
                _kpi("Live Pipelines", live, ICO_CHART),
                _kpi("Avg Quality", round(avg_q, 1), ICO_AI, suffix="%"),
                _kpi("Stale Pipelines", len(health) - live, ICO_PIPE),
            ], className="g-2 mb-3"),
            html.Div([
                html.Div("AI-READY PIPELINE STATUS", style={"color": WHITE, "fontSize": "0.78rem", "fontWeight": "600", "marginBottom": "8px"}),
                dbc.Table([
                    html.Thead(html.Tr([html.Th("Table"), html.Th("Rows"), html.Th("Last Updated"), html.Th("Status"), html.Th("Quality")])),
                    html.Tbody(rows),
                ], bordered=True, hover=True, striped=True, size="sm"),
            ], style={"background": CARD, "borderRadius": "8px", "padding": "14px", "border": f"1px solid {BORDER}"}),
        ], style={"padding": "16px 20px"}),
    ])


# ═══════════════════════════════════════════
# PAGE: SUPPORT
# ═══════════════════════════════════════════
def support_page():
    df = backend.get_zendesk_summary()
    rows = [html.Tr([
        html.Td(r["category"], style={"color": WHITE}),
        html.Td(f'{int(r["ticket_count"]):,}', style={"color": WHITE}),
        html.Td(f'{r["avg_resolution_hours"]}h', style={"color": MUTED}),
        html.Td(f'{r["satisfaction_pct"]}%', style={"color": GREEN if r["satisfaction_pct"] > 85 else AMBER}),
    ]) for _, r in df.iterrows()]
    return html.Div([
        top_bar("Support Analytics"),
        html.Div([
            dbc.Table([
                html.Thead(html.Tr([html.Th("Category"), html.Th("Tickets"), html.Th("Avg Resolution"), html.Th("Satisfaction")])),
                html.Tbody(rows),
            ], bordered=True, hover=True, striped=True, size="sm"),
        ], style={"padding": "16px 20px", "background": CARD, "borderRadius": "8px", "margin": "16px 20px", "border": f"1px solid {BORDER}"}),
    ])


# ── Layout ──
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    sidebar(),
    html.Div(id="page-content", style={"marginLeft": "210px", "background": BG, "minHeight": "100vh"}),
], style={"fontFamily": "'Inter', 'Segoe UI', system-ui, sans-serif", "fontSize": "13px"})


@callback(Output("page-content", "children"), Input("url", "pathname"))
def route(path):
    pages = {"/": command_center, "/revenue": revenue_page, "/seats": seats_page,
             "/fans": fans_page, "/matches": matches_page, "/pipeline": pipeline_page, "/support": support_page}
    return [pages.get(path, command_center)()]


# ═══════════════════════════════════════════
# CALLBACKS — Charts
# ═══════════════════════════════════════════

@callback(Output("chart-rev-trend", "figure"), Input("url", "pathname"))
def _rev_trend(_):
    df = backend.get_revenue_trend()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["month"], y=df["revenue"], marker_color=ACCENT, name="Revenue", opacity=0.7))
    fig.add_trace(go.Scatter(x=df["month"], y=df["tickets"], yaxis="y2", mode="lines+markers",
                             line=dict(color=GREEN, width=2), marker=dict(size=5), name="Tickets"))
    fig.update_layout(**_CL, showlegend=True, legend=dict(font=dict(size=9), x=0, y=1.15, orientation="h"),
                      yaxis2=dict(overlaying="y", side="right", showgrid=False, gridcolor=BORDER))
    return fig


@callback(Output("chart-comp-split", "figure"), Input("url", "pathname"))
def _comp_split(_):
    df = backend.get_competition_breakdown()
    fig = go.Figure(go.Pie(labels=df["competition"], values=df["revenue"], hole=0.55,
                           marker=dict(colors=[ACCENT, "#34d399", "#fbbf24", "#a78bfa"]),
                           textinfo="label+percent", textfont=dict(size=9, color=WHITE)))
    fig.update_layout(**_CL, showlegend=False)
    return fig


@callback(Output("chart-channels", "figure"), Input("url", "pathname"))
def _channels(_):
    df = backend.get_sale_channels()
    fig = go.Figure(go.Bar(y=df["channel"], x=df["tickets"], orientation="h", marker_color=ACCENT,
                           text=[f'{p}%' for p in df["pct"]], textposition="outside", textfont=dict(color=WHITE, size=9)))
    fig.update_layout(**_CL)
    fig.update_xaxes(showticklabels=False)
    return fig


@callback(Output("chart-age", "figure"), Input("url", "pathname"))
def _age(_):
    df = backend.get_attenders_age()
    fig = go.Figure(go.Bar(x=df["age_band"], y=df["percentage"], marker_color=ACCENT,
                           text=[f'{v}%' for v in df["percentage"]], textposition="outside", textfont=dict(color=WHITE, size=9)))
    fig.update_layout(**_CL)
    fig.update_yaxes(showticklabels=False, range=[0, max(df["percentage"]) * 1.3])
    fig.update_xaxes(tickangle=-45, tickfont=dict(size=8))
    return fig


@callback(Output("chart-oneoff", "figure"), Input("url", "pathname"))
def _oneoff(_):
    d = backend.get_one_off_attenders()
    fig = go.Figure(go.Indicator(mode="gauge+number", value=d["total"],
        number=dict(font=dict(size=28, color=WHITE), valueformat=",.1s"),
        gauge=dict(axis=dict(range=[0, d["max_range"]], tickfont=dict(size=7), tickcolor=MUTED),
                   bar=dict(color=ACCENT), bgcolor=CARD, bordercolor=CARD,
                   steps=[dict(range=[0, d["max_range"]*0.5], color=BG), dict(range=[d["max_range"]*0.5, d["max_range"]], color=CARD)])))
    fig.add_annotation(x=0.22, y=0.08, text=f'FIRST TIMER<br><b>{d["first_timer_pct"]}%</b>', showarrow=False, font=dict(size=9, color=MUTED))
    fig.add_annotation(x=0.78, y=0.08, text=f'AVG PRICE<br><b>£{d["avg_ticket_cost"]}</b>', showarrow=False, font=dict(size=9, color=MUTED))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=MUTED), margin=dict(l=16, r=16, t=20, b=4))
    return fig


@callback(Output("chart-rev-match", "figure"), Input("url", "pathname"))
def _rev_match(_):
    df = backend.get_revenue_by_match()
    colors = [ACCENT if c == "PL" else (GREEN if c == "UCL" else AMBER) for c in df["competition"]]
    fig = go.Figure(go.Bar(x=df["match"], y=df["revenue"], marker_color=colors,
                           text=[f'£{v/1e6:.1f}M' for v in df["revenue"]], textposition="outside", textfont=dict(size=7, color=WHITE)))
    fig.update_layout(**_CL)
    fig.update_xaxes(tickangle=-60, tickfont=dict(size=7))
    fig.update_yaxes(showticklabels=False)
    return fig


@callback(Output("chart-price-dist", "figure"), Input("url", "pathname"))
def _price_dist(_):
    df = backend.get_price_distribution()
    fig = go.Figure(go.Bar(x=df["price_band"], y=df["count"], marker_color=ACCENT,
                           text=[f'{v/1000:.0f}K' for v in df["count"]], textposition="outside", textfont=dict(size=9, color=WHITE)))
    fig.update_layout(**_CL)
    fig.update_yaxes(showticklabels=False)
    return fig


@callback(Output("chart-seat-heat", "figure"), Input("url", "pathname"))
def _seat_heat(_):
    df = backend.get_section_occupancy()
    fig = go.Figure(go.Bar(y=df["section"], x=df["avg_occupancy_pct"], orientation="h",
                           marker=dict(color=df["avg_occupancy_pct"], colorscale=[[0, RED], [0.5, AMBER], [1, GREEN]], cmin=80, cmax=100),
                           text=[f'{v}%' for v in df["avg_occupancy_pct"]], textposition="outside", textfont=dict(size=9, color=WHITE)))
    fig.update_layout(**_CL, margin=dict(l=140, r=30, t=8, b=20))
    fig.update_xaxes(range=[75, 105], showticklabels=False)
    return fig


@callback(Output("chart-seat-dist", "figure"), Input("url", "pathname"))
def _seat_dist(_):
    df = backend.get_section_occupancy()
    fig = go.Figure(go.Scatter(x=df["avg_occupancy_pct"], y=df["avg_revenue"], mode="markers+text",
                               text=df["section"].str[:8], textposition="top center", textfont=dict(size=7, color=MUTED),
                               marker=dict(size=df["capacity"]/300, color=ACCENT, opacity=0.7)))
    fig.update_layout(**_CL)
    fig.update_xaxes(title="Occupancy %", title_font=dict(size=9))
    fig.update_yaxes(title="Revenue (£)", title_font=dict(size=9))
    return fig


@callback(Output("chart-segments", "figure"), Input("url", "pathname"))
def _segments(_):
    df = backend.get_buyer_segments()
    fig = go.Figure(go.Treemap(labels=df["segment"], parents=[""] * len(df), values=df["fans"],
                               textinfo="label+value", textfont=dict(size=11),
                               marker=dict(colors=[ACCENT, GREEN, AMBER, "#a78bfa", "#f472b6", MUTED])))
    fig.update_layout(**_CL, margin=dict(l=4, r=4, t=4, b=4))
    return fig


@callback(Output("chart-distance", "figure"), Input("url", "pathname"))
def _distance(_):
    df = backend.get_attenders_distance()
    fig = go.Figure(go.Bar(x=df["percentage"], y=df["distance_band"], orientation="h", marker_color=ACCENT,
                           text=[f'{v}%' for v in df["percentage"]], textposition="outside", textfont=dict(size=10, color=WHITE)))
    fig.update_layout(**_CL)
    fig.update_xaxes(range=[0, max(df["percentage"]) * 1.35], showticklabels=False)
    fig.update_yaxes(title="Miles from stadium", title_font=dict(size=9, color=MUTED))
    return fig


@callback(Output("chart-gender", "figure"), Input("url", "pathname"))
def _gender(_):
    df = backend.get_attenders_gender()
    fig = go.Figure(go.Pie(labels=df["gender"], values=df["percentage"], hole=0.6,
                           marker=dict(colors=[ACCENT, GREEN]), textinfo="label+percent", textfont=dict(size=10, color=WHITE)))
    fig.update_layout(**_CL, showlegend=False)
    return fig


@callback(Output("chart-countries", "figure"), Input("url", "pathname"))
def _countries(_):
    df = backend.get_attenders_country()
    fig = go.Figure(go.Bar(x=df["percentage"], y=df["country"], orientation="h", marker_color=ACCENT,
                           text=[f'{v}%' for v in df["percentage"]], textposition="outside", textfont=dict(size=9, color=WHITE)))
    fig.update_layout(**_CL)
    fig.update_xaxes(range=[0, max(df["percentage"]) * 1.4], showticklabels=False)
    return fig


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
