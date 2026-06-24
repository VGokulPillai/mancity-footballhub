"""Man City Fan Intelligence Hub — Dash Application.

Pixel-accurate replica of the Power BI Fan Intelligence Hub dashboard,
built on Databricks with Dash + Plotly.
"""

import os
import datetime
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from backend import get_backend

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True,
    title="Fan Intelligence Hub",
)
server = app.server

# -- Exact Power BI colour palette --
NAVY = "#1a2332"
SIDEBAR_BG = "#1e293b"
PANEL_BG = "#1e293b"
CONTENT_BG = "#111a27"
CITY_BLUE = "#6CADDF"
TEXT_WHITE = "#FFFFFF"
TEXT_MUTED = "#94a3b8"
BORDER = "#2a3a4e"

backend = get_backend()

SEASONS = ["25/26", "24/25", "23/24", "22/23"]
COMPETITIONS = ["All", "Premier League", "Champions League", "FA Cup", "League Cup"]

# -- SVG icon strings (inline, no emoji) --
SVG_PEOPLE = '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="#6CADDF" viewBox="0 0 24 24"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5s-3 1.34-3 3 1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>'
SVG_CHART = '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="#6CADDF" viewBox="0 0 24 24"><path d="M3.5 18.49l6-6.01 4 4L22 6.92l-1.41-1.41-7.09 7.97-4-4L2 16.99z"/></svg>'
SVG_TICKET = '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="#6CADDF" viewBox="0 0 24 24"><path d="M22 10V6a2 2 0 00-2-2H4a2 2 0 00-2 2v4a2 2 0 010 4v4a2 2 0 002 2h16a2 2 0 002-2v-4a2 2 0 010-4zm-2-1.46a4 4 0 000 6.92V18H4v-2.54a4 4 0 000-6.92V6h16v2.54z"/></svg>'
SVG_MONEY = '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="#6CADDF" viewBox="0 0 24 24"><path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/></svg>'
SVG_PERSON = '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="#6CADDF" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>'
SVG_FILTER = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#6CADDF" viewBox="0 0 24 24"><path d="M10 18h4v-2h-4v2zM3 6v2h18V6H3zm3 7h12v-2H6v2z"/></svg>'
SVG_BACK = '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="#6CADDF" viewBox="0 0 24 24"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/></svg>'
SVG_INFO = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="#6CADDF" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>'


def _icon(svg_str):
    return html.Div(
        dangerously_allow_html=True,
        children="",
        style={"display": "inline-block"},
        **{"data-dash-is-loading": False},
    ) if False else html.Iframe(
        srcDoc=svg_str,
        style={"width": "24px", "height": "24px", "border": "none", "overflow": "hidden", "verticalAlign": "middle"},
    )


def make_kpi_card(title, value, svg_icon, prefix="", suffix=""):
    if isinstance(value, float) and value == int(value):
        value = int(value)
    if isinstance(value, int) and value >= 1000:
        if value >= 1_000_000:
            display_val = f"{prefix}{value:,.0f}"
        else:
            display_val = f"{prefix}{value:,}{suffix}"
    elif isinstance(value, float):
        display_val = f"{prefix}{value}{suffix}"
    else:
        display_val = f"{prefix}{value}{suffix}"

    return dbc.Col(html.Div([
        _icon(svg_icon),
        html.Div(title, style={
            "fontSize": "0.65rem", "color": TEXT_MUTED, "textTransform": "uppercase",
            "letterSpacing": "1px", "marginTop": "2px", "fontWeight": "500",
        }),
        html.Div(display_val, style={
            "fontSize": "1.35rem", "fontWeight": "700", "color": TEXT_WHITE, "marginTop": "2px",
        }),
    ], style={"textAlign": "center", "padding": "12px 4px"}), width=True)


def _dropdown(label, did, options, default):
    return html.Div([
        html.Label(label, style={"color": TEXT_MUTED, "fontSize": "0.72rem", "fontWeight": "500", "marginBottom": "2px"}),
        dcc.Dropdown(id=did, options=[{"label": o, "value": o} for o in options], value=default,
                     clearable=False, style={"fontSize": "0.78rem", "backgroundColor": "#1e293b"}),
    ], style={"marginBottom": "8px"})


def filters_col():
    return html.Div([
        html.Div([
            _icon(SVG_FILTER),
            html.Span(" RESET FILTERS", style={"color": CITY_BLUE, "fontSize": "0.8rem", "fontWeight": "600", "marginLeft": "4px", "verticalAlign": "middle"}),
        ], style={"marginBottom": "14px", "cursor": "pointer"}),

        _dropdown("Season", "filter-season", SEASONS, "25/26"),
        _dropdown("Away Team", "filter-away-team", ["All"], "All"),
        _dropdown("Competition", "filter-competition", COMPETITIONS, "All"),
        _dropdown("Match", "filter-match", ["All"], "All"),

        html.Label("Event Date", style={"color": TEXT_MUTED, "fontSize": "0.72rem", "fontWeight": "500", "marginBottom": "2px"}),
        dcc.DatePickerRange(
            id="filter-date-range",
            start_date="2025-08-23",
            end_date="2026-06-24",
            display_format="DD/MM/YYYY",
            style={"fontSize": "0.75rem", "marginBottom": "8px"},
        ),

        _dropdown("Ticket Area", "filter-ticket-area", ["All"], "All"),
        html.Label("One Off / Season Ticket", style={"color": TEXT_MUTED, "fontSize": "0.72rem", "fontWeight": "500", "marginBottom": "2px"}),
        dcc.Dropdown(id="filter-oneoff-season", options=[{"label": o, "value": o} for o in ["All", "One Off", "Season Ticket"]],
                     value="All", clearable=False, style={"fontSize": "0.78rem", "marginBottom": "8px"}),
        _dropdown("Price Type", "filter-price-type", ["All"], "All"),
        _dropdown("Seat Location", "filter-seat-location", ["All"], "All"),
        _dropdown("Sale Method", "filter-sale-method", ["All"], "All"),
    ], style={"padding": "0 10px 10px 0", "minWidth": "180px"})


# -- Sidebar (matches Power BI exactly) --
def _nav_item(label, href, active=False, indent=0, icon_char=None, has_chevron=False):
    style = {
        "color": TEXT_WHITE if active else TEXT_MUTED,
        "fontSize": "0.82rem", "padding": "7px 16px",
        "paddingLeft": f"{16 + indent}px",
        "display": "flex", "alignItems": "center", "gap": "8px",
        "textDecoration": "none", "borderLeft": f"3px solid {CITY_BLUE}" if active else "3px solid transparent",
        "background": "rgba(108,173,223,0.08)" if active else "transparent",
        "fontWeight": "600" if active else "400",
    }
    chevron = html.Span("›", style={"marginLeft": "auto", "fontSize": "1rem"}) if has_chevron else None
    icon = html.Span(icon_char, style={"fontSize": "0.9rem"}) if icon_char else None
    children = [icon, html.Span(label)]
    if chevron:
        children.append(chevron)
    return html.A(children, href=href, style=style)


def sidebar():
    return html.Div([
        html.Div([
            html.Img(src="/assets/mancity-crest.png", style={"height": "50px", "marginBottom": "4px"}),
            html.Div("Fan Intelligence Hub", style={"color": TEXT_WHITE, "fontWeight": "700", "fontSize": "0.9rem", "marginTop": "4px"}),
        ], style={"textAlign": "center", "padding": "18px 16px 12px"}),

        html.Div([
            _nav_item("Home", "/"),
            html.Div([
                _nav_item("KPIs", "#", icon_char="", has_chevron=True),
                html.Div([
                    _nav_item("Matchday", "#", has_chevron=True, indent=16),
                    html.Div([
                        _nav_item("Matchday", "/matchday", active=True, indent=32),
                    ]),
                ]),
            ]),
            _nav_item("Zendesk", "/zendesk", has_chevron=True),
            _nav_item("Facilities Matchday KPIs", "/facilities"),
            _nav_item("Matchday Feedback", "#", has_chevron=True),
            html.Div([
                _nav_item("Matchday Fan Feedba...", "/feedback", indent=16, icon_char=""),
            ]),
            _nav_item("Product", "/product", has_chevron=True),
            _nav_item("Merchandise", "/merchandise", has_chevron=True),
        ], style={"flex": "1"}),

        html.A([
            html.Span("←", style={"marginRight": "6px"}),
            html.Span("Go back"),
        ], href="/", style={
            "color": TEXT_MUTED, "fontSize": "0.82rem", "padding": "14px 16px",
            "textDecoration": "none", "display": "block", "borderTop": f"1px solid {BORDER}",
        }),
    ], style={
        "background": SIDEBAR_BG, "width": "200px", "minHeight": "100vh",
        "display": "flex", "flexDirection": "column",
        "position": "fixed", "left": 0, "top": 0, "zIndex": 1000,
        "borderRight": f"1px solid {BORDER}",
    })


def top_bar():
    return html.Div([
        html.Div([
            html.Img(src="/assets/mancity-crest.png", style={"height": "24px", "marginRight": "10px"}),
            html.Span("Matchday", style={"fontWeight": "600", "color": TEXT_WHITE, "fontSize": "0.95rem"}),
            html.Span(
                f"Data updated {datetime.date.today().strftime('%d/%m/%y')}",
                style={"color": TEXT_MUTED, "fontSize": "0.75rem", "marginLeft": "14px"},
            ),
        ], style={"display": "flex", "alignItems": "center"}),
        html.Div([
            html.Div("Search", style={
                "color": TEXT_MUTED, "fontSize": "0.8rem", "background": NAVY,
                "border": f"1px solid {BORDER}", "borderRadius": "4px",
                "padding": "4px 40px 4px 12px",
            }),
        ]),
    ], style={
        "display": "flex", "justifyContent": "space-between", "alignItems": "center",
        "padding": "10px 20px", "background": NAVY, "borderBottom": f"1px solid {BORDER}",
    })


# ── Matchday page (exact Power BI layout) ──
def matchday_page():
    return html.Div([
        # KPI banner
        html.Div([
            html.Div([_icon(SVG_BACK), html.Span("BACK", style={"color": TEXT_MUTED, "fontSize": "0.8rem", "fontWeight": "600", "marginLeft": "6px", "verticalAlign": "middle"})],
                     style={"display": "inline-flex", "alignItems": "center", "cursor": "pointer"}),
        ], style={"marginBottom": "10px"}),

        dbc.Row(id="kpi-row", className="g-2 mb-3",
                style={"background": PANEL_BG, "borderRadius": "6px", "padding": "6px 0", "margin": "0"}),

        # Main 2-column: filters left, charts right
        html.Div([
            html.Div(filters_col(), style={"width": "210px", "flexShrink": 0}),
            html.Div([
                # Row 1: Age + Distance
                dbc.Row([
                    dbc.Col([
                        html.Div("ATTENDERS - AGE", style={"color": TEXT_WHITE, "fontSize": "0.8rem", "fontWeight": "600", "marginBottom": "4px"}),
                        dcc.Graph(id="chart-age", config={"displayModeBar": False}, style={"height": "240px"}),
                    ], md=6),
                    dbc.Col([
                        html.Div("ATTENDERS - DISTANCE", style={"color": TEXT_WHITE, "fontSize": "0.8rem", "fontWeight": "600", "marginBottom": "4px"}),
                        dcc.Graph(id="chart-distance", config={"displayModeBar": False}, style={"height": "240px"}),
                    ], md=6),
                ], className="g-3 mb-3"),

                # Row 2: Gender + Outside UK + One-Off gauge
                dbc.Row([
                    dbc.Col([
                        html.Div("ATTENDERS - GENDER", style={"color": TEXT_WHITE, "fontSize": "0.8rem", "fontWeight": "600", "marginBottom": "4px"}),
                        dcc.Graph(id="chart-gender", config={"displayModeBar": False}, style={"height": "220px"}),
                    ], md=4),
                    dbc.Col([
                        html.Div("ATTENDERS - OUTSIDE UK", style={"color": TEXT_WHITE, "fontSize": "0.8rem", "fontWeight": "600", "marginBottom": "4px"}),
                        dcc.Graph(id="chart-outside-uk", config={"displayModeBar": False}, style={"height": "220px"}),
                    ], md=4),
                    dbc.Col([
                        html.Div([
                            html.Span("ONE OFF TICKET ATTENDERS", style={"color": TEXT_WHITE, "fontSize": "0.8rem", "fontWeight": "600"}),
                            html.Span(style={"marginLeft": "6px", "display": "inline-block"}),
                            _icon(SVG_INFO),
                        ], style={"marginBottom": "4px", "display": "flex", "alignItems": "center"}),
                        dcc.Graph(id="chart-oneoff", config={"displayModeBar": False}, style={"height": "220px"}),
                    ], md=4),
                ], className="g-3"),
            ], style={"flex": 1, "minWidth": 0}),
        ], style={"display": "flex", "gap": "16px"}),
    ], style={"padding": "16px 20px"})


# ── Other pages ──
def home_page():
    return html.Div([
        html.Div([
            html.Div([
                html.Img(src="/assets/etihad-stadium.png",
                         style={"width": "100%", "borderRadius": "10px", "opacity": "0.25",
                                "position": "absolute", "top": 0, "left": 0, "height": "100%", "objectFit": "cover"}),
                html.Div([
                    html.H2("Fan Intelligence Hub", style={"color": TEXT_WHITE, "fontWeight": "700"}),
                    html.P("Comprehensive matchday analytics powered by Databricks",
                           style={"color": TEXT_MUTED, "fontSize": "1rem"}),
                ], style={"position": "relative", "zIndex": 1}),
            ], style={"position": "relative", "padding": "50px 36px", "borderRadius": "10px",
                       "overflow": "hidden", "background": PANEL_BG}),
        ], className="mb-4"),
        dbc.Row([
            _home_card("Matchday", "Attendance, ticketing revenue, demographics, and distance analysis", "/matchday"),
            _home_card("Zendesk", "Customer support tickets, categories, and resolution metrics", "/zendesk"),
            _home_card("Merchandise", "Retail transactions, product performance, and revenue analytics", "/merchandise"),
        ], className="g-3 mb-3"),
        dbc.Row([
            _home_card("Facilities KPIs", "Capacity utilization, dwell time, and food & beverage revenue", "/facilities"),
            _home_card("Product / Membership", "Membership transactions, City+ subscriptions, and engagement data", "/product"),
            _home_card("Data Tables", "View all underlying Unity Catalog tables and their connection status", "/tables"),
        ], className="g-3"),
    ], style={"padding": "20px"})


def _home_card(title, desc, href):
    return dbc.Col(dbc.Card(dbc.CardBody([
        html.H5(title, style={"color": CITY_BLUE, "fontWeight": "600"}),
        html.P(desc, style={"color": TEXT_MUTED, "fontSize": "0.82rem"}),
        dbc.Button("View \u2192", href=href, color="info", outline=True, size="sm"),
    ]), style={"background": PANEL_BG, "border": f"1px solid {BORDER}"}), md=4)


def data_tables_page():
    tables = backend.list_tables()
    rows = [html.Tr([
        html.Td(t["table"], style={"color": TEXT_WHITE, "fontSize": "0.82rem"}),
        html.Td(t["catalog"], style={"color": TEXT_MUTED, "fontSize": "0.82rem"}),
        html.Td(t["schema"], style={"color": TEXT_MUTED, "fontSize": "0.82rem"}),
        html.Td(dbc.Badge(t["status"], color="success" if t["status"] == "live" else "warning")),
    ]) for t in tables]
    return html.Div([
        html.H4("Data Tables", style={"color": TEXT_WHITE, "marginBottom": "14px"}),
        html.P(f"Catalog: {os.getenv('DATABRICKS_CATALOG', 'algatty_manchester_usr_gp')} | Schema: {os.getenv('DATABRICKS_SCHEMA', 'default')}",
               style={"color": TEXT_MUTED, "fontSize": "0.82rem"}),
        dbc.Table([
            html.Thead(html.Tr([html.Th("Table"), html.Th("Catalog"), html.Th("Schema"), html.Th("Status")])),
            html.Tbody(rows),
        ], bordered=True, hover=True, striped=True, className="mt-2"),
    ], style={"padding": "20px"})


def zendesk_page():
    summary = backend.get_zendesk_summary()
    rows = [html.Tr([
        html.Td(r["category"], style={"color": TEXT_WHITE}),
        html.Td(f"{int(r['ticket_count']):,}", style={"color": TEXT_WHITE}),
        html.Td(f"{r['avg_resolution_hours']}h", style={"color": TEXT_MUTED}),
        html.Td(f"{r['satisfaction_pct']}%", style={"color": CITY_BLUE}),
    ]) for _, r in summary.iterrows()]
    return html.Div([
        html.H4("Zendesk Support Analytics", style={"color": TEXT_WHITE, "marginBottom": "16px"}),
        dbc.Table([
            html.Thead(html.Tr([html.Th("Category"), html.Th("Tickets"), html.Th("Avg Resolution"), html.Th("Satisfaction")])),
            html.Tbody(rows),
        ], bordered=True, hover=True, striped=True),
    ], style={"padding": "20px"})


def merchandise_page():
    r = backend.get_retail_summary()
    return html.Div([
        html.H4("Merchandise & Retail", style={"color": TEXT_WHITE, "marginBottom": "16px"}),
        dbc.Row([
            make_kpi_card("Revenue", r["total_revenue"], SVG_MONEY, prefix="\u00a3"),
            make_kpi_card("Transactions", r["total_transactions"], SVG_TICKET),
            make_kpi_card("Avg Basket", r["avg_basket_size"], SVG_MONEY, prefix="\u00a3"),
            make_kpi_card("Top Category", r["top_category"], SVG_CHART),
        ], className="g-3"),
    ], style={"padding": "20px"})


def facilities_page():
    k = backend.get_facilities_kpis()
    return html.Div([
        html.H4("Facilities Matchday KPIs", style={"color": TEXT_WHITE, "marginBottom": "16px"}),
        dbc.Row([
            make_kpi_card("Capacity Utilization", k["capacity_utilization"], SVG_CHART, suffix="%"),
            make_kpi_card("Avg Dwell Time", k["avg_dwell_time_mins"], SVG_CHART, suffix=" min"),
            make_kpi_card("F&B Revenue", k["food_bev_revenue"], SVG_MONEY, prefix="\u00a3"),
            make_kpi_card("Incidents", k["incidents_reported"], SVG_INFO),
        ], className="g-3"),
    ], style={"padding": "20px"})


def product_page():
    m = backend.get_membership_summary()
    e = backend.get_engagement_summary()
    t = backend.get_tour_summary()
    return html.Div([
        html.H4("Product & Membership", style={"color": TEXT_WHITE, "marginBottom": "16px"}),
        html.H5("Membership", style={"color": CITY_BLUE, "marginTop": "16px", "marginBottom": "8px"}),
        dbc.Row([make_kpi_card("Total Members", m["total_members"], SVG_PEOPLE),
                 make_kpi_card("Revenue", m["revenue"], SVG_MONEY, prefix="\u00a3")], className="g-3 mb-3"),
        html.H5("Fan Engagement", style={"color": CITY_BLUE, "marginTop": "16px", "marginBottom": "8px"}),
        dbc.Row([make_kpi_card("Total Engagements", e["total_engagements"], SVG_CHART),
                 make_kpi_card("Unique Fans", e["unique_fans_engaged"], SVG_PEOPLE),
                 make_kpi_card("Top Channel", e["top_channel"], SVG_CHART),
                 make_kpi_card("Avg per Fan", e["avg_engagements_per_fan"], SVG_PERSON)], className="g-3 mb-3"),
        html.H5("Stadium Tours", style={"color": CITY_BLUE, "marginTop": "16px", "marginBottom": "8px"}),
        dbc.Row([make_kpi_card("Total Tours", t["total_tours"], SVG_TICKET),
                 make_kpi_card("Revenue", t["revenue"], SVG_MONEY, prefix="\u00a3"),
                 make_kpi_card("Avg Group Size", t["avg_group_size"], SVG_PEOPLE)], className="g-3"),
    ], style={"padding": "20px"})


# ── Layout ──
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    sidebar(),
    html.Div([
        top_bar(),
        html.Div(id="page-content"),
    ], style={"marginLeft": "200px", "background": CONTENT_BG, "minHeight": "100vh"}),
], style={"fontFamily": "'Segoe UI', 'Inter', system-ui, sans-serif", "fontSize": "14px"})


# ── Routing ──
@callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    pages = {
        "/matchday": matchday_page, "/zendesk": zendesk_page,
        "/merchandise": merchandise_page, "/facilities": facilities_page,
        "/product": product_page, "/tables": data_tables_page,
    }
    return [pages.get(pathname, home_page)()]


# ── KPIs ──
@callback(Output("kpi-row", "children"), Input("filter-season", "value"))
def update_kpis(season):
    k = backend.get_matchday_kpis(season=season)
    return [
        make_kpi_card("ATTENDERS", k["attenders"], SVG_PEOPLE),
        make_kpi_card("ATTENDANCE", k["attendance_pct"], SVG_CHART, suffix="%"),
        make_kpi_card("TICKETS SOLD", k["tickets_sold"], SVG_TICKET),
        make_kpi_card("TICKETING REVENUE", k["ticketing_revenue"], SVG_MONEY, prefix="\u00a3"),
        make_kpi_card("UNIQUE BUYERS", k["unique_buyers"], SVG_PERSON),
    ]


# ── Chart layout base ──
_CL = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=TEXT_MUTED, size=11),
    margin=dict(l=40, r=16, t=8, b=36),
    xaxis=dict(gridcolor="#1e293b", showgrid=False),
    yaxis=dict(gridcolor="#1e293b", showgrid=False),
)


@callback(Output("chart-age", "figure"), Input("filter-season", "value"))
def update_age_chart(season):
    df = backend.get_attenders_age(season=season)
    fig = go.Figure(go.Bar(
        x=df["age_band"], y=df["percentage"], marker_color=CITY_BLUE,
        text=[f"{v}%" for v in df["percentage"]], textposition="outside",
        textfont=dict(color=TEXT_WHITE, size=10),
    ))
    fig.update_layout(**_CL)
    fig.update_yaxes(range=[0, max(df["percentage"]) * 1.35], showticklabels=False)
    fig.update_xaxes(tickangle=-45, tickfont=dict(size=9))
    return fig


@callback(Output("chart-distance", "figure"), Input("filter-season", "value"))
def update_distance_chart(season):
    df = backend.get_attenders_distance(season=season)
    fig = go.Figure(go.Bar(
        x=df["percentage"], y=df["distance_band"], orientation="h", marker_color=CITY_BLUE,
        text=[f"{v}%" for v in df["percentage"]], textposition="outside",
        textfont=dict(color=TEXT_WHITE, size=10),
    ))
    fig.update_layout(**_CL)
    fig.update_xaxes(range=[0, max(df["percentage"]) * 1.35], showticklabels=False)
    fig.update_yaxes(title_text="Miles from stadium", title_font=dict(size=9, color=TEXT_MUTED), tickfont=dict(size=9))
    return fig


@callback(Output("chart-gender", "figure"), Input("filter-season", "value"))
def update_gender_chart(season):
    df = backend.get_attenders_gender(season=season)
    fig = go.Figure(go.Bar(
        y=df["gender"], x=df["percentage"], orientation="h",
        marker_color=CITY_BLUE,
        text=[f"{v}%" for v in df["percentage"]], textposition="outside",
        textfont=dict(color=TEXT_WHITE, size=11), width=0.45,
    ))
    fig.update_layout(**_CL)
    fig.update_xaxes(range=[0, 100], showticklabels=False)
    fig.update_yaxes(tickfont=dict(size=10))
    return fig


@callback(Output("chart-outside-uk", "figure"), Input("filter-season", "value"))
def update_outside_uk_chart(season):
    df = backend.get_attenders_outside_uk(season=season)
    fig = go.Figure(go.Bar(
        x=df["percentage"], y=df["country"], orientation="h", marker_color=CITY_BLUE,
        text=[f"{v}%" for v in df["percentage"]], textposition="outside",
        textfont=dict(color=TEXT_WHITE, size=10),
    ))
    fig.update_layout(**_CL)
    fig.update_xaxes(range=[0, max(df["percentage"]) * 1.4 if len(df) > 0 else 25], showticklabels=False)
    fig.update_yaxes(tickfont=dict(size=9))
    return fig


@callback(Output("chart-oneoff", "figure"), Input("filter-season", "value"))
def update_oneoff_chart(season):
    d = backend.get_one_off_ticket_attenders(season=season)
    total, mx = d["total"], d["max_range"]
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=total,
        number=dict(font=dict(size=32, color=TEXT_WHITE), valueformat=",.1s"),
        gauge=dict(
            axis=dict(range=[0, mx], tickcolor=TEXT_MUTED, tickfont=dict(size=8)),
            bar=dict(color=CITY_BLUE), bgcolor="#1e293b", bordercolor="#1e293b",
            steps=[dict(range=[0, mx * 0.5], color="#1a2332"), dict(range=[mx * 0.5, mx], color="#1e293b")],
        ),
    ))
    fig.add_annotation(x=0.22, y=0.12, text=f"FIRST TIMER %<br><b>{d['first_timer_pct']}%</b>",
                       showarrow=False, font=dict(size=10, color=TEXT_MUTED), align="center")
    fig.add_annotation(x=0.78, y=0.12, text=f"AVG TICKET COST<br><b>\u00a3{d['avg_ticket_cost']}</b>",
                       showarrow=False, font=dict(size=10, color=TEXT_MUTED), align="center")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(color=TEXT_MUTED), margin=dict(l=20, r=20, t=24, b=8))
    return fig


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
