"""Man City Fan Intelligence Hub — Dash Application.

A comprehensive matchday analytics dashboard built on Databricks,
mirroring the Fan Intelligence Hub with KPIs, demographics, and
operational insights.
"""

import os
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px

from backend import get_backend

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True,
    title="Fan Intelligence Hub",
)
server = app.server

CITY_BLUE = "#6CADDF"
DARK_BG = "#1B2838"
CARD_BG = "#243447"
TEXT_WHITE = "#FFFFFF"
TEXT_MUTED = "#8CA0B3"
ACCENT_CYAN = "#00C9DB"

backend = get_backend()

SEASONS = ["25/26", "24/25", "23/24", "22/23"]
COMPETITIONS = ["All", "Premier League", "Champions League", "FA Cup", "League Cup"]


def make_kpi_card(title, value, icon="", prefix="", suffix=""):
    display_val = f"{prefix}{value:,}{suffix}" if isinstance(value, (int, float)) else f"{prefix}{value}{suffix}"
    return dbc.Col(
        html.Div([
            html.Div(icon, style={"fontSize": "1.4rem", "color": CITY_BLUE, "marginBottom": "4px"}),
            html.Div(title, style={"fontSize": "0.7rem", "color": TEXT_MUTED, "textTransform": "uppercase", "letterSpacing": "0.5px"}),
            html.Div(display_val, style={"fontSize": "1.5rem", "fontWeight": "700", "color": TEXT_WHITE}),
        ], style={
            "textAlign": "center",
            "padding": "16px 8px",
            "background": CARD_BG,
            "borderRadius": "8px",
            "border": f"1px solid {DARK_BG}",
        }),
        width=True,
    )


def chart_card(title, chart_id, height=300):
    return html.Div([
        html.H6(title, style={"color": TEXT_WHITE, "fontWeight": "600", "marginBottom": "12px", "fontSize": "0.85rem"}),
        dcc.Graph(id=chart_id, config={"displayModeBar": False}, style={"height": f"{height}px"}),
    ], style={
        "background": CARD_BG,
        "borderRadius": "8px",
        "padding": "20px",
        "height": "100%",
    })


def filters_panel():
    return html.Div([
        html.Div([
            html.Img(
                src="/assets/mancity-crest.png",
                style={"height": "60px", "marginBottom": "8px"},
            ) if os.path.exists("assets/mancity-crest.png") else html.Div(),
            html.H5("Fan Intelligence Hub", style={"color": TEXT_WHITE, "fontWeight": "700", "marginBottom": "24px"}),
        ], style={"textAlign": "center"}),

        html.Hr(style={"borderColor": "#3A4F65"}),

        _filter_group("Season", "filter-season", SEASONS, SEASONS[0]),
        _filter_group("Away Team", "filter-away-team", ["All"], "All"),
        _filter_group("Competition", "filter-competition", COMPETITIONS, "All"),
        _filter_group("Match", "filter-match", ["All"], "All"),

        html.Label("Event Date", style={"color": TEXT_MUTED, "fontSize": "0.75rem", "marginTop": "12px"}),
        dcc.DatePickerRange(
            id="filter-date-range",
            start_date="2025-08-01",
            end_date="2026-06-30",
            style={"width": "100%"},
        ),

        _filter_group("Ticket Area", "filter-ticket-area", ["All", "One Off / Season Ticket"], "All"),
        _filter_group("Price Type", "filter-price-type", ["All"], "All"),
        _filter_group("Seat Location", "filter-seat-location", ["All"], "All"),
        _filter_group("Sale Method", "filter-sale-method", ["All"], "All"),

        html.Div([
            dbc.Button("Reset Filters", id="btn-reset", color="info", outline=True, size="sm", className="mt-3 w-100"),
        ]),

    ], style={
        "background": DARK_BG,
        "padding": "20px",
        "borderRadius": "8px",
        "overflowY": "auto",
        "maxHeight": "calc(100vh - 60px)",
    })


def _filter_group(label, dropdown_id, options, default):
    return html.Div([
        html.Label(label, style={"color": TEXT_MUTED, "fontSize": "0.75rem", "marginTop": "12px"}),
        dcc.Dropdown(
            id=dropdown_id,
            options=[{"label": o, "value": o} for o in options],
            value=default,
            clearable=False,
            style={"fontSize": "0.8rem"},
        ),
    ])


NAV_ITEMS = [
    {"label": "Home", "href": "/"},
    {"label": "KPIs", "children": [
        {"label": "Matchday", "href": "/matchday"},
    ]},
    {"label": "Zendesk", "href": "/zendesk"},
    {"label": "Facilities Matchday KPIs", "href": "/facilities"},
    {"label": "Matchday Feedback", "href": "/feedback"},
    {"label": "Product", "href": "/product"},
    {"label": "Merchandise", "href": "/merchandise"},
]


def sidebar():
    items = []
    for nav in NAV_ITEMS:
        if "children" in nav:
            children = [
                dbc.NavLink(c["label"], href=c["href"], style={"color": TEXT_MUTED, "paddingLeft": "28px", "fontSize": "0.8rem"})
                for c in nav["children"]
            ]
            items.append(html.Div([
                html.Div(nav["label"], style={"color": TEXT_WHITE, "padding": "8px 16px", "fontWeight": "600", "fontSize": "0.85rem"}),
                *children,
            ]))
        else:
            items.append(
                dbc.NavLink(nav["label"], href=nav["href"], style={"color": TEXT_WHITE, "fontSize": "0.85rem"})
            )

    return html.Div([
        html.Div([
            html.Img(
                src="/assets/mancity-crest.png",
                style={"height": "48px", "marginRight": "10px"},
            ) if os.path.exists("assets/mancity-crest.png") else html.Div(),
            html.Span("Fan Intelligence Hub", style={"color": TEXT_WHITE, "fontWeight": "700", "fontSize": "1rem"}),
        ], style={"display": "flex", "alignItems": "center", "padding": "16px", "borderBottom": f"1px solid {CARD_BG}"}),
        dbc.Nav(items, vertical=True, className="mt-2"),
        html.Div([
            html.A("← Go back", href="/", style={"color": TEXT_MUTED, "fontSize": "0.8rem", "textDecoration": "none"}),
        ], style={"padding": "16px", "marginTop": "auto"}),
    ], style={
        "background": DARK_BG,
        "width": "220px",
        "minHeight": "100vh",
        "display": "flex",
        "flexDirection": "column",
        "position": "fixed",
        "left": 0,
        "top": 0,
        "zIndex": 1000,
        "borderRight": f"1px solid {CARD_BG}",
    })


def top_bar():
    return html.Div([
        html.Div([
            html.Span("Matchday", style={"fontWeight": "600", "color": TEXT_WHITE, "fontSize": "1rem"}),
            html.Span(
                f"  Data updated {__import__('datetime').date.today().strftime('%d/%m/%y')}",
                style={"color": TEXT_MUTED, "fontSize": "0.75rem", "marginLeft": "16px"},
            ),
        ], style={"display": "flex", "alignItems": "center"}),
        html.Div([
            html.Img(
                src="/assets/databricks-logo.png",
                style={"height": "28px"},
            ) if os.path.exists("assets/databricks-logo.png") else html.Div(),
        ]),
    ], style={
        "display": "flex",
        "justifyContent": "space-between",
        "alignItems": "center",
        "padding": "12px 24px",
        "background": DARK_BG,
        "borderBottom": f"1px solid {CARD_BG}",
        "marginLeft": "220px",
    })


def matchday_page():
    return html.Div([
        dbc.Row([
            dbc.Col(filters_panel(), width=3),
            dbc.Col([
                dbc.Row(id="kpi-row", className="g-3 mb-4"),

                dbc.Row([
                    dbc.Col(chart_card("ATTENDERS — AGE", "chart-age"), md=6),
                    dbc.Col(chart_card("ATTENDERS — DISTANCE", "chart-distance"), md=6),
                ], className="g-3 mb-4"),

                dbc.Row([
                    dbc.Col(chart_card("ATTENDERS — GENDER", "chart-gender"), md=4),
                    dbc.Col(chart_card("ATTENDERS — OUTSIDE UK", "chart-outside-uk"), md=4),
                    dbc.Col(chart_card("ONE OFF TICKET ATTENDERS", "chart-oneoff"), md=4),
                ], className="g-3"),
            ], width=9),
        ]),
    ], style={"padding": "24px"})


def data_tables_page():
    tables = backend.list_tables()
    rows = []
    for t in tables:
        rows.append(html.Tr([
            html.Td(t["table"], style={"color": TEXT_WHITE}),
            html.Td(t["catalog"], style={"color": TEXT_MUTED}),
            html.Td(t["schema"], style={"color": TEXT_MUTED}),
            html.Td(
                dbc.Badge(t["status"], color="success" if t["status"] == "live" else "warning"),
            ),
        ]))

    return html.Div([
        html.H4("Data Tables", style={"color": TEXT_WHITE, "marginBottom": "16px"}),
        html.P(f"Catalog: {os.getenv('DATABRICKS_CATALOG', 'algatty_manchester_usr_gp')} | Schema: {os.getenv('DATABRICKS_SCHEMA', 'default')}",
               style={"color": TEXT_MUTED, "fontSize": "0.85rem"}),
        dbc.Table([
            html.Thead(html.Tr([
                html.Th("Table"),
                html.Th("Catalog"),
                html.Th("Schema"),
                html.Th("Status"),
            ])),
            html.Tbody(rows),
        ], bordered=True, hover=True, striped=True, className="mt-3"),
    ], style={"padding": "24px"})


def home_page():
    return html.Div([
        html.Div([
            html.Div([
                html.Img(
                    src="/assets/etihad-stadium.png",
                    style={"width": "100%", "borderRadius": "12px", "opacity": "0.3", "position": "absolute", "top": 0, "left": 0, "height": "100%", "objectFit": "cover"},
                ) if os.path.exists("assets/etihad-stadium.png") else html.Div(),
                html.Div([
                    html.H2("Fan Intelligence Hub", style={"color": TEXT_WHITE, "fontWeight": "700"}),
                    html.P("Comprehensive matchday analytics powered by Databricks", style={"color": TEXT_MUTED, "fontSize": "1rem"}),
                ], style={"position": "relative", "zIndex": 1}),
            ], style={"position": "relative", "padding": "60px 40px", "borderRadius": "12px", "overflow": "hidden", "background": CARD_BG}),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H5("Matchday", style={"color": CITY_BLUE}),
                    html.P("Attendance, ticketing revenue, demographics, and distance analysis", style={"color": TEXT_MUTED, "fontSize": "0.85rem"}),
                    dbc.Button("View →", href="/matchday", color="info", outline=True, size="sm"),
                ]),
            ], style={"background": CARD_BG, "border": "none"}), md=4),

            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H5("Zendesk", style={"color": CITY_BLUE}),
                    html.P("Customer support tickets, categories, and resolution metrics", style={"color": TEXT_MUTED, "fontSize": "0.85rem"}),
                    dbc.Button("View →", href="/zendesk", color="info", outline=True, size="sm"),
                ]),
            ], style={"background": CARD_BG, "border": "none"}), md=4),

            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H5("Merchandise", style={"color": CITY_BLUE}),
                    html.P("Retail transactions, product performance, and revenue analytics", style={"color": TEXT_MUTED, "fontSize": "0.85rem"}),
                    dbc.Button("View →", href="/merchandise", color="info", outline=True, size="sm"),
                ]),
            ], style={"background": CARD_BG, "border": "none"}), md=4),
        ], className="g-3 mb-4"),

        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H5("Facilities KPIs", style={"color": CITY_BLUE}),
                    html.P("Capacity utilization, dwell time, and food & beverage revenue", style={"color": TEXT_MUTED, "fontSize": "0.85rem"}),
                    dbc.Button("View →", href="/facilities", color="info", outline=True, size="sm"),
                ]),
            ], style={"background": CARD_BG, "border": "none"}), md=4),

            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H5("Product / Membership", style={"color": CITY_BLUE}),
                    html.P("Membership transactions, City+ subscriptions, and engagement data", style={"color": TEXT_MUTED, "fontSize": "0.85rem"}),
                    dbc.Button("View →", href="/product", color="info", outline=True, size="sm"),
                ]),
            ], style={"background": CARD_BG, "border": "none"}), md=4),

            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H5("Data Tables", style={"color": CITY_BLUE}),
                    html.P("View all underlying Unity Catalog tables and their connection status", style={"color": TEXT_MUTED, "fontSize": "0.85rem"}),
                    dbc.Button("View →", href="/tables", color="info", outline=True, size="sm"),
                ]),
            ], style={"background": CARD_BG, "border": "none"}), md=4),
        ], className="g-3"),
    ], style={"padding": "24px"})


def zendesk_page():
    summary = backend.get_zendesk_summary()
    rows = []
    for _, r in summary.iterrows():
        rows.append(html.Tr([
            html.Td(r["category"], style={"color": TEXT_WHITE}),
            html.Td(f"{int(r['ticket_count']):,}", style={"color": TEXT_WHITE}),
            html.Td(f"{r['avg_resolution_hours']}h", style={"color": TEXT_MUTED}),
            html.Td(f"{r['satisfaction_pct']}%", style={"color": CITY_BLUE}),
        ]))

    return html.Div([
        html.H4("Zendesk Support Analytics", style={"color": TEXT_WHITE, "marginBottom": "20px"}),
        dbc.Table([
            html.Thead(html.Tr([html.Th("Category"), html.Th("Tickets"), html.Th("Avg Resolution"), html.Th("Satisfaction")])),
            html.Tbody(rows),
        ], bordered=True, hover=True, striped=True),
    ], style={"padding": "24px"})


def merchandise_page():
    retail = backend.get_retail_summary()
    return html.Div([
        html.H4("Merchandise & Retail", style={"color": TEXT_WHITE, "marginBottom": "20px"}),
        dbc.Row([
            make_kpi_card("Revenue", retail["total_revenue"], prefix="£"),
            make_kpi_card("Transactions", retail["total_transactions"]),
            make_kpi_card("Avg Basket", retail["avg_basket_size"], prefix="£"),
            make_kpi_card("Top Category", retail["top_category"]),
        ], className="g-3"),
    ], style={"padding": "24px"})


def facilities_page():
    kpis = backend.get_facilities_kpis()
    return html.Div([
        html.H4("Facilities Matchday KPIs", style={"color": TEXT_WHITE, "marginBottom": "20px"}),
        dbc.Row([
            make_kpi_card("Capacity Utilization", kpis["capacity_utilization"], suffix="%"),
            make_kpi_card("Avg Dwell Time", kpis["avg_dwell_time_mins"], suffix=" min"),
            make_kpi_card("F&B Revenue", kpis["food_bev_revenue"], prefix="£"),
            make_kpi_card("Incidents", kpis["incidents_reported"]),
        ], className="g-3"),
    ], style={"padding": "24px"})


def product_page():
    membership = backend.get_membership_summary()
    engagement = backend.get_engagement_summary()
    tour = backend.get_tour_summary()

    return html.Div([
        html.H4("Product & Membership", style={"color": TEXT_WHITE, "marginBottom": "20px"}),

        html.H5("Membership", style={"color": CITY_BLUE, "marginTop": "24px", "marginBottom": "12px"}),
        dbc.Row([
            make_kpi_card("Total Members", membership["total_members"]),
            make_kpi_card("Revenue", membership["revenue"], prefix="£"),
        ], className="g-3 mb-4"),

        html.H5("Fan Engagement", style={"color": CITY_BLUE, "marginTop": "24px", "marginBottom": "12px"}),
        dbc.Row([
            make_kpi_card("Total Engagements", engagement["total_engagements"]),
            make_kpi_card("Unique Fans", engagement["unique_fans_engaged"]),
            make_kpi_card("Top Channel", engagement["top_channel"]),
            make_kpi_card("Avg per Fan", engagement["avg_engagements_per_fan"]),
        ], className="g-3 mb-4"),

        html.H5("Stadium Tours", style={"color": CITY_BLUE, "marginTop": "24px", "marginBottom": "12px"}),
        dbc.Row([
            make_kpi_card("Total Tours", tour["total_tours"]),
            make_kpi_card("Revenue", tour["revenue"], prefix="£"),
            make_kpi_card("Avg Group Size", tour["avg_group_size"]),
        ], className="g-3"),
    ], style={"padding": "24px"})


app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    sidebar(),
    html.Div([
        top_bar(),
        html.Div(id="page-content"),
    ], style={"marginLeft": "220px", "background": "#0F1923", "minHeight": "100vh"}),
], style={"fontFamily": "'Inter', 'Segoe UI', sans-serif"})


@callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/matchday":
        return [matchday_page()]
    elif pathname == "/zendesk":
        return [zendesk_page()]
    elif pathname == "/merchandise":
        return [merchandise_page()]
    elif pathname == "/facilities":
        return [facilities_page()]
    elif pathname == "/product":
        return [product_page()]
    elif pathname == "/tables":
        return [data_tables_page()]
    return [home_page()]


@callback(Output("kpi-row", "children"), Input("filter-season", "value"))
def update_kpis(season):
    kpis = backend.get_matchday_kpis(season=season)
    return [
        make_kpi_card("ATTENDERS", kpis["attenders"], icon="👥"),
        make_kpi_card("ATTENDANCE", kpis["attendance_pct"], icon="📊", suffix="%"),
        make_kpi_card("TICKETS SOLD", kpis["tickets_sold"], icon="🎫"),
        make_kpi_card("TICKETING REVENUE", kpis["ticketing_revenue"], icon="💰", prefix="£"),
        make_kpi_card("UNIQUE BUYERS", kpis["unique_buyers"], icon="👤"),
    ]


CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=TEXT_MUTED, size=11),
    margin=dict(l=40, r=20, t=10, b=40),
    xaxis=dict(gridcolor="#2A3F55"),
    yaxis=dict(gridcolor="#2A3F55"),
)


@callback(Output("chart-age", "figure"), Input("filter-season", "value"))
def update_age_chart(season):
    df = backend.get_attenders_age(season=season)
    fig = go.Figure(go.Bar(
        x=df["age_band"],
        y=df["percentage"],
        marker_color=CITY_BLUE,
        text=[f"{v}%" for v in df["percentage"]],
        textposition="outside",
        textfont=dict(color=TEXT_WHITE, size=11),
    ))
    fig.update_layout(**CHART_LAYOUT)
    fig.update_yaxes(title_text="% of attenders", range=[0, max(df["percentage"]) * 1.3])
    return fig


@callback(Output("chart-distance", "figure"), Input("filter-season", "value"))
def update_distance_chart(season):
    df = backend.get_attenders_distance(season=season)
    fig = go.Figure(go.Bar(
        x=df["percentage"],
        y=df["distance_band"],
        orientation="h",
        marker_color=CITY_BLUE,
        text=[f"{v}%" for v in df["percentage"]],
        textposition="outside",
        textfont=dict(color=TEXT_WHITE, size=11),
    ))
    fig.update_layout(**CHART_LAYOUT)
    fig.update_xaxes(title_text="% of attenders", range=[0, max(df["percentage"]) * 1.4])
    fig.update_yaxes(title_text="Miles from stadium")
    return fig


@callback(Output("chart-gender", "figure"), Input("filter-season", "value"))
def update_gender_chart(season):
    df = backend.get_attenders_gender(season=season)
    fig = go.Figure(go.Bar(
        x=df["gender"],
        y=df["percentage"],
        marker_color=[CITY_BLUE, ACCENT_CYAN],
        text=[f"{v}%" for v in df["percentage"]],
        textposition="outside",
        textfont=dict(color=TEXT_WHITE, size=12),
        width=0.5,
    ))
    fig.update_layout(**CHART_LAYOUT)
    fig.update_yaxes(range=[0, 100])
    return fig


@callback(Output("chart-outside-uk", "figure"), Input("filter-season", "value"))
def update_outside_uk_chart(season):
    df = backend.get_attenders_outside_uk(season=season)
    fig = go.Figure(go.Bar(
        x=df["percentage"],
        y=df["country"],
        orientation="h",
        marker_color=CITY_BLUE,
        text=[f"{v}%" for v in df["percentage"]],
        textposition="outside",
        textfont=dict(color=TEXT_WHITE, size=11),
    ))
    fig.update_layout(**CHART_LAYOUT)
    fig.update_xaxes(range=[0, max(df["percentage"]) * 1.4 if len(df) > 0 else 30])
    return fig


@callback(Output("chart-oneoff", "figure"), Input("filter-season", "value"))
def update_oneoff_chart(season):
    data = backend.get_one_off_ticket_attenders(season=season)
    total = data["total"]
    max_range = data["max_range"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=total,
        number=dict(font=dict(size=36, color=TEXT_WHITE), valueformat=",.0f"),
        gauge=dict(
            axis=dict(range=[0, max_range], tickcolor=TEXT_MUTED),
            bar=dict(color=CITY_BLUE),
            bgcolor=CARD_BG,
            bordercolor=CARD_BG,
            steps=[
                dict(range=[0, max_range * 0.5], color="#1B2838"),
                dict(range=[max_range * 0.5, max_range], color="#243447"),
            ],
        ),
    ))

    fig.add_annotation(
        x=0.25, y=0.15, text=f"FIRST TIMER %<br><b>{data['first_timer_pct']}%</b>",
        showarrow=False, font=dict(size=11, color=TEXT_MUTED), align="center",
    )
    fig.add_annotation(
        x=0.75, y=0.15, text=f"AVG TICKET COST<br><b>£{data['avg_ticket_cost']}</b>",
        showarrow=False, font=dict(size=11, color=TEXT_MUTED), align="center",
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_MUTED),
        margin=dict(l=30, r=30, t=30, b=10),
    )
    return fig


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
