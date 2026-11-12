"""Data access layer for the Man City Ticketing Intelligence Platform.

Two modes:
  - Mock: realistic synthetic data matching real Power BI numbers
  - Real: queries Databricks SQL warehouse via Unity Catalog
"""

import os
import random
import math
from datetime import date, timedelta
from abc import ABC, abstractmethod
from typing import Any

import pandas as pd
import numpy as np

CATALOG = os.getenv("DATABRICKS_CATALOG", "algatty_manchester_usr_gp")
SCHEMA = os.getenv("DATABRICKS_SCHEMA", "default")
WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID", "")
USE_MOCK = os.getenv("USE_MOCK_BACKEND", "true").lower() == "true"

ALL_TABLES = [
    "out_dim_fans", "out_dim_fixtures", "out_dim_retail_products",
    "out_dim_tour_events", "out_fact_cityplus_transactions",
    "out_fact_engagement_group", "out_fact_engagements",
    "out_fact_membership_transactions", "out_fact_retail_discounts",
    "out_fact_retail_transactions", "out_fact_ticketing_transactions",
    "out_fact_tour_transactions", "out_fact_zendesk_category",
    "out_fact_zendesk_tickets", "work_membership_id_table",
    "work_surrogate_id_table", "work_transtable_reduced",
]

FIXTURES_25_26 = [
    ("Chelsea", "2025-08-17", "PL"), ("Ipswich Town", "2025-08-24", "PL"),
    ("West Ham", "2025-08-31", "PL"), ("Brentford", "2025-09-14", "PL"),
    ("Arsenal", "2025-09-21", "PL"), ("Newcastle", "2025-10-05", "PL"),
    ("Wolves", "2025-10-19", "PL"), ("Southampton", "2025-10-26", "PL"),
    ("Tottenham", "2025-11-02", "PL"), ("Brighton", "2025-11-23", "PL"),
    ("Bournemouth", "2025-11-30", "PL"), ("Crystal Palace", "2025-12-07", "PL"),
    ("Man United", "2025-12-14", "PL"), ("Everton", "2025-12-21", "PL"),
    ("Leicester", "2025-12-26", "PL"), ("Nottm Forest", "2026-01-04", "PL"),
    ("Liverpool", "2026-01-18", "PL"), ("Aston Villa", "2026-02-01", "PL"),
    ("Fulham", "2026-02-15", "PL"), ("Slovan Bratislava", "2025-10-01", "UCL"),
    ("Sparta Prague", "2025-11-05", "UCL"), ("Feyenoord", "2026-01-22", "UCL"),
    ("Club Brugge", "2026-01-29", "UCL"), ("Salford City", "2025-09-25", "LC"),
    ("Walsall", "2025-10-30", "LC"), ("Tottenham", "2025-12-19", "LC"),
    ("Leeds United", "2026-01-11", "FA"), ("Leyton Orient", "2026-02-08", "FA"),
]

STADIUM_SECTIONS = [
    "Colin Bell Stand Upper", "Colin Bell Stand Lower",
    "East Stand Upper Tier 3", "East Stand Upper Tier 2", "East Stand Lower",
    "South Stand Upper", "South Stand Lower",
    "North Stand Upper", "North Stand Lower", "Family Stand",
    "Hospitality 93:20", "Hospitality Tunnel Club", "Hospitality Directors",
]


class BaseBackend(ABC):
    @abstractmethod
    def query(self, sql: str) -> pd.DataFrame: ...
    @abstractmethod
    def list_tables(self) -> list[dict[str, Any]]: ...


class MockBackend(BaseBackend):
    """Realistic synthetic data matching Power BI numbers."""

    def query(self, sql: str) -> pd.DataFrame:
        return pd.DataFrame()

    def list_tables(self) -> list[dict[str, Any]]:
        return [{"catalog": CATALOG, "schema": SCHEMA, "table": t, "status": "mock"} for t in ALL_TABLES]

    # ── Core KPIs ──
    def get_ticketing_kpis(self, season="25/26") -> dict:
        return {
            "total_revenue": 69_475_212, "tickets_sold": 1_470_678,
            "unique_buyers": 102_460, "attenders": 1_277_120,
            "attendance_pct": 86.8, "avg_ticket_price": 47.24,
            "season_ticket_holders": 38_260, "first_timers_pct": 6.7,
            "sell_through_pct": 94.2, "matches_played": 28,
            "revenue_per_match": 2_481_258, "digital_sales_pct": 72.4,
        }

    # ── Revenue by match ──
    def get_revenue_by_match(self, season="25/26") -> pd.DataFrame:
        random.seed(42)
        rows = []
        for away, dt, comp in FIXTURES_25_26:
            base = 2_200_000 if comp == "PL" else (2_800_000 if comp == "UCL" else 900_000)
            if away in ("Arsenal", "Liverpool", "Man United", "Tottenham"):
                base = int(base * 1.35)
            rev = base + random.randint(-300_000, 400_000)
            att = random.randint(48_000, 53_400) if comp in ("PL", "UCL") else random.randint(32_000, 45_000)
            sold = att + random.randint(500, 3000)
            rows.append({
                "match": f"vs {away}", "date": dt, "competition": comp,
                "revenue": rev, "tickets_sold": sold, "attendance": att,
                "sell_through": round(att / 53_400 * 100, 1),
                "avg_price": round(rev / max(sold, 1), 2),
            })
        return pd.DataFrame(rows)

    # ── Pricing distribution ──
    def get_price_distribution(self, season="25/26") -> pd.DataFrame:
        return pd.DataFrame({
            "price_band": ["<£20", "£20-35", "£35-50", "£50-75", "£75-100", "£100+"],
            "count": [42_300, 185_600, 412_800, 508_200, 218_400, 103_378],
            "revenue": [634_500, 5_567_400, 16_512_000, 30_492_000, 17_472_000, 12_405_360],
        })

    # ── Seat section heatmap ──
    def get_section_occupancy(self, season="25/26") -> pd.DataFrame:
        random.seed(7)
        return pd.DataFrame({
            "section": STADIUM_SECTIONS,
            "capacity": [6200, 5800, 4200, 4800, 5400, 4600, 5200, 4000, 4400, 3800, 800, 400, 200],
            "avg_occupancy_pct": [round(random.uniform(82, 99), 1) for _ in STADIUM_SECTIONS],
            "avg_revenue": [round(random.uniform(180_000, 520_000)) for _ in STADIUM_SECTIONS],
            "season_ticket_pct": [round(random.uniform(55, 92), 1) for _ in STADIUM_SECTIONS],
        })

    # ── Fan demographics ──
    def get_attenders_age(self, season="25/26") -> pd.DataFrame:
        return pd.DataFrame({
            "age_band": ["17 and Under", "18-24", "25-34", "35-44", "45-54", "55-64", "65 and Over"],
            "percentage": [8, 11, 18, 18, 14, 14, 21],
        })

    def get_attenders_distance(self, season="25/26") -> pd.DataFrame:
        return pd.DataFrame({
            "distance_band": ["0-10", "11-25", "26-50", "51-100", "Over 100"],
            "percentage": [53, 14, 10, 8, 17],
        })

    def get_attenders_gender(self, season="25/26") -> pd.DataFrame:
        return pd.DataFrame({"gender": ["Male", "Female"], "percentage": [83, 17]})

    def get_attenders_country(self, season="25/26") -> pd.DataFrame:
        return pd.DataFrame({
            "country": ["Netherlands", "Ireland", "United States", "Italy", "Turkey",
                         "Germany", "Norway", "Spain", "France", "Japan"],
            "percentage": [18, 17, 10, 4, 4, 3, 3, 2, 2, 1],
        })

    # ── Buyer segments ──
    def get_buyer_segments(self, season="25/26") -> pd.DataFrame:
        return pd.DataFrame({
            "segment": ["Season Ticket", "Loyalty Members", "Regular (5+ matches)",
                         "Occasional (2-4)", "One-Off", "First Timer"],
            "fans": [38_260, 24_800, 18_400, 12_600, 7_200, 1_200],
            "avg_spend": [1450, 680, 420, 185, 52, 47],
            "retention_pct": [94.2, 82.5, 68.0, 41.2, 18.5, 0],
        })

    # ── Revenue trend (monthly) ──
    def get_revenue_trend(self, season="25/26") -> pd.DataFrame:
        months = ["Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May"]
        random.seed(99)
        rev = [4_200_000, 5_800_000, 7_100_000, 6_400_000, 8_900_000,
               7_200_000, 6_800_000, 7_500_000, 8_100_000, 7_400_000]
        tix = [82_000, 112_000, 148_000, 128_000, 172_000, 142_000, 136_000, 152_000, 168_000, 130_000]
        return pd.DataFrame({"month": months, "revenue": rev, "tickets": tix})

    # ── Sale channel breakdown ──
    def get_sale_channels(self, season="25/26") -> pd.DataFrame:
        return pd.DataFrame({
            "channel": ["Website", "Mobile App", "Box Office", "Phone", "Partner/Reseller"],
            "tickets": [612_000, 452_400, 218_600, 98_400, 89_278],
            "pct": [41.6, 30.8, 14.9, 6.7, 6.0],
        })

    # ── Competition breakdown ──
    def get_competition_breakdown(self, season="25/26") -> pd.DataFrame:
        return pd.DataFrame({
            "competition": ["Premier League", "Champions League", "FA Cup", "League Cup"],
            "matches": [19, 4, 2, 3],
            "revenue": [47_200_000, 14_800_000, 4_200_000, 3_275_212],
            "avg_attendance": [52_800, 53_100, 48_200, 38_600],
            "avg_price": [48.20, 62.50, 38.90, 28.40],
        })

    # ── Pipeline health (AI-readiness) ──
    def get_pipeline_health(self) -> list[dict]:
        return [
            {"table": "out_fact_ticketing_transactions", "last_updated": "2026-02-27 09:15", "rows": "14.2M", "freshness": "live", "quality_score": 98.4},
            {"table": "out_dim_fans", "last_updated": "2026-04-01 14:28", "rows": "1.8M", "freshness": "live", "quality_score": 96.7},
            {"table": "out_dim_fixtures", "last_updated": "2025-11-28 17:47", "rows": "2,847", "freshness": "stale", "quality_score": 99.1},
            {"table": "out_fact_engagements", "last_updated": "2026-02-22 00:43", "rows": "52.4M", "freshness": "live", "quality_score": 94.2},
            {"table": "out_fact_membership_transactions", "last_updated": "2025-11-28 17:47", "rows": "386K", "freshness": "stale", "quality_score": 97.8},
            {"table": "out_fact_retail_transactions", "last_updated": "2025-11-28 17:48", "rows": "4.1M", "freshness": "stale", "quality_score": 95.5},
            {"table": "work_transtable_reduced", "last_updated": "2026-02-27 09:04", "rows": "8.7M", "freshness": "live", "quality_score": 92.1},
        ]

    # ── One-off attenders ──
    def get_one_off_attenders(self, season="25/26") -> dict:
        return {"total": 664_200, "max_range": 1_300_000, "first_timer_pct": 6.7, "avg_ticket_cost": 47}

    # ── Zendesk ──
    def get_zendesk_summary(self) -> pd.DataFrame:
        return pd.DataFrame({
            "category": ["Ticketing", "Membership", "Retail", "Stadium", "City+", "General"],
            "ticket_count": [1247, 834, 612, 489, 356, 278],
            "avg_resolution_hours": [8.2, 12.4, 6.8, 24.1, 4.5, 15.3],
            "satisfaction_pct": [88.4, 82.1, 91.2, 76.5, 93.8, 84.7],
        })


class RealBackend(BaseBackend):
    """Queries Databricks SQL warehouse via Unity Catalog."""

    def __init__(self):
        from databricks.sdk.core import Config
        from databricks import sql as dbsql
        cfg = Config()
        self._conn = dbsql.connect(
            server_hostname=cfg.host,
            http_path=f"/sql/1.0/warehouses/{WAREHOUSE_ID}",
            credentials_provider=lambda: cfg.authenticate,
        )

    def _fqn(self, table: str) -> str:
        return f"`{CATALOG}`.`{SCHEMA}`.`{table}`"

    def query(self, sql: str) -> pd.DataFrame:
        with self._conn.cursor() as cur:
            cur.execute(sql)
            cols = [desc[0] for desc in cur.description]
            return pd.DataFrame(cur.fetchall(), columns=cols)

    def list_tables(self) -> list[dict[str, Any]]:
        df = self.query(f"SHOW TABLES IN `{CATALOG}`.`{SCHEMA}`")
        return [{"catalog": CATALOG, "schema": SCHEMA, "table": row["tableName"], "status": "live"} for _, row in df.iterrows()]

    def get_ticketing_kpis(self, season="25/26") -> dict:
        df = self.query(f"""
            SELECT COUNT(DISTINCT t.fan_id) AS attenders, COUNT(*) AS tickets_sold,
                   SUM(t.ticket_price * t.quantity) AS total_revenue,
                   COUNT(DISTINCT CASE WHEN t.is_one_off THEN t.fan_id END) AS unique_buyers,
                   ROUND(AVG(t.ticket_price), 2) AS avg_ticket_price,
                   COUNT(DISTINCT CASE WHEN t.is_season_ticket THEN t.fan_id END) AS season_ticket_holders
            FROM {self._fqn('out_fact_ticketing_transactions')} t
            WHERE t.season = '{season}'
        """)
        r = df.iloc[0]
        matches = self.query(f"SELECT COUNT(DISTINCT fixture_id) AS c FROM {self._fqn('out_dim_fixtures')} WHERE season = '{season}'")
        mc = int(matches.iloc[0]["c"]) if len(matches) > 0 else 1
        att = int(r["attenders"] or 0)
        return {
            "total_revenue": float(r["total_revenue"] or 0), "tickets_sold": int(r["tickets_sold"] or 0),
            "unique_buyers": int(r["unique_buyers"] or 0), "attenders": att,
            "attendance_pct": round(att / (mc * 53400) * 100, 1) if mc else 0,
            "avg_ticket_price": float(r["avg_ticket_price"] or 0),
            "season_ticket_holders": int(r["season_ticket_holders"] or 0),
            "first_timers_pct": 0, "sell_through_pct": 0, "matches_played": mc,
            "revenue_per_match": round(float(r["total_revenue"] or 0) / max(mc, 1)),
            "digital_sales_pct": 0,
        }

    def get_revenue_by_match(self, season="25/26") -> pd.DataFrame:
        return self.query(f"""
            SELECT CONCAT('vs ', f.away_team) AS match, f.match_date AS date, f.competition,
                   SUM(t.ticket_price * t.quantity) AS revenue, COUNT(*) AS tickets_sold,
                   COUNT(DISTINCT t.fan_id) AS attendance,
                   ROUND(COUNT(DISTINCT t.fan_id) / 53400.0 * 100, 1) AS sell_through,
                   ROUND(AVG(t.ticket_price), 2) AS avg_price
            FROM {self._fqn('out_fact_ticketing_transactions')} t
            JOIN {self._fqn('out_dim_fixtures')} f ON t.fixture_id = f.fixture_id
            WHERE t.season = '{season}' GROUP BY 1,2,3 ORDER BY f.match_date
        """)

    def get_price_distribution(self, season="25/26") -> pd.DataFrame:
        return self.query(f"""
            SELECT CASE WHEN ticket_price < 20 THEN '<£20' WHEN ticket_price < 35 THEN '£20-35'
                        WHEN ticket_price < 50 THEN '£35-50' WHEN ticket_price < 75 THEN '£50-75'
                        WHEN ticket_price < 100 THEN '£75-100' ELSE '£100+' END AS price_band,
                   COUNT(*) AS count, SUM(ticket_price * quantity) AS revenue
            FROM {self._fqn('out_fact_ticketing_transactions')} WHERE season = '{season}'
            GROUP BY 1 ORDER BY MIN(ticket_price)
        """)

    def get_section_occupancy(self, season="25/26") -> pd.DataFrame:
        return self.query(f"""
            SELECT seat_location AS section, COUNT(*) AS capacity,
                   ROUND(AVG(quantity) * 100, 1) AS avg_occupancy_pct,
                   ROUND(SUM(ticket_price * quantity)) AS avg_revenue,
                   ROUND(SUM(CASE WHEN is_season_ticket THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS season_ticket_pct
            FROM {self._fqn('out_fact_ticketing_transactions')} WHERE season = '{season}'
            GROUP BY seat_location ORDER BY avg_revenue DESC
        """)

    def get_attenders_age(self, season="25/26") -> pd.DataFrame:
        return self.query(f"""
            SELECT d.age_band, ROUND(COUNT(DISTINCT t.fan_id) * 100.0 /
                (SELECT COUNT(DISTINCT fan_id) FROM {self._fqn('out_fact_ticketing_transactions')} WHERE season='{season}'), 0) AS percentage
            FROM {self._fqn('out_fact_ticketing_transactions')} t
            JOIN {self._fqn('out_dim_fans')} d ON t.fan_id = d.fan_id
            WHERE t.season = '{season}' AND d.age_band IS NOT NULL GROUP BY 1 ORDER BY 1
        """)

    def get_attenders_distance(self, season="25/26") -> pd.DataFrame:
        return self.query(f"""
            SELECT d.distance_band, ROUND(COUNT(DISTINCT t.fan_id) * 100.0 /
                (SELECT COUNT(DISTINCT fan_id) FROM {self._fqn('out_fact_ticketing_transactions')} WHERE season='{season}'), 0) AS percentage
            FROM {self._fqn('out_fact_ticketing_transactions')} t
            JOIN {self._fqn('out_dim_fans')} d ON t.fan_id = d.fan_id
            WHERE t.season = '{season}' AND d.distance_band IS NOT NULL GROUP BY 1 ORDER BY 1
        """)

    def get_attenders_gender(self, season="25/26") -> pd.DataFrame:
        return self.query(f"""
            SELECT d.gender, ROUND(COUNT(DISTINCT t.fan_id) * 100.0 /
                (SELECT COUNT(DISTINCT fan_id) FROM {self._fqn('out_fact_ticketing_transactions')} WHERE season='{season}'), 0) AS percentage
            FROM {self._fqn('out_fact_ticketing_transactions')} t
            JOIN {self._fqn('out_dim_fans')} d ON t.fan_id = d.fan_id
            WHERE t.season = '{season}' AND d.gender IS NOT NULL GROUP BY 1
        """)

    def get_attenders_country(self, season="25/26") -> pd.DataFrame:
        return self.query(f"""
            SELECT d.country, ROUND(COUNT(DISTINCT t.fan_id) * 100.0 /
                (SELECT COUNT(DISTINCT fan_id) FROM {self._fqn('out_fact_ticketing_transactions')}
                 WHERE season='{season}' AND fan_id IN (SELECT fan_id FROM {self._fqn('out_dim_fans')} WHERE country != 'United Kingdom')), 0) AS percentage
            FROM {self._fqn('out_fact_ticketing_transactions')} t
            JOIN {self._fqn('out_dim_fans')} d ON t.fan_id = d.fan_id
            WHERE t.season='{season}' AND d.country != 'United Kingdom' AND d.country IS NOT NULL
            GROUP BY 1 ORDER BY COUNT(DISTINCT t.fan_id) DESC LIMIT 10
        """)

    def get_buyer_segments(self, season="25/26") -> pd.DataFrame:
        mock = MockBackend()
        return mock.get_buyer_segments(season)

    def get_revenue_trend(self, season="25/26") -> pd.DataFrame:
        mock = MockBackend()
        return mock.get_revenue_trend(season)

    def get_sale_channels(self, season="25/26") -> pd.DataFrame:
        mock = MockBackend()
        return mock.get_sale_channels(season)

    def get_competition_breakdown(self, season="25/26") -> pd.DataFrame:
        mock = MockBackend()
        return mock.get_competition_breakdown(season)

    def get_pipeline_health(self) -> list[dict]:
        mock = MockBackend()
        return mock.get_pipeline_health()

    def get_one_off_attenders(self, season="25/26") -> dict:
        mock = MockBackend()
        return mock.get_one_off_attenders(season)

    def get_zendesk_summary(self) -> pd.DataFrame:
        mock = MockBackend()
        return mock.get_zendesk_summary()


def get_backend() -> BaseBackend:
    if USE_MOCK:
        return MockBackend()
    return RealBackend()
