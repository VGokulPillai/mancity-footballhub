"""Data access layer for the Man City Fan Intelligence Hub.

Supports two modes:
  - Mock backend: returns realistic synthetic data for local development
  - Real backend: queries Databricks SQL warehouse via Unity Catalog
"""

import os
import random
from datetime import date, timedelta
from abc import ABC, abstractmethod
from typing import Any

import pandas as pd

CATALOG = os.getenv("DATABRICKS_CATALOG", "algatty_manchester_usr_gp")
SCHEMA = os.getenv("DATABRICKS_SCHEMA", "default")
WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID", "")
USE_MOCK = os.getenv("USE_MOCK_BACKEND", "true").lower() == "true"

ALL_TABLES = [
    "out_dim_fans",
    "out_dim_fixtures",
    "out_dim_retail_products",
    "out_dim_tour_events",
    "out_fact_cityplus_transactions",
    "out_fact_engagement_group",
    "out_fact_engagements",
    "out_fact_membership_transactions",
    "out_fact_retail_discounts",
    "out_fact_retail_transactions",
    "out_fact_ticketing_transactions",
    "out_fact_tour_transactions",
    "out_fact_zendesk_category",
    "out_fact_zendesk_tickets",
    "work_membership_id_table",
    "work_surrogate_id_table",
    "work_transtable_reduced",
]


class BaseBackend(ABC):
    @abstractmethod
    def query(self, sql: str) -> pd.DataFrame:
        ...

    @abstractmethod
    def list_tables(self) -> list[dict[str, Any]]:
        ...

    def get_matchday_kpis(self, season: str, event_date_start: str, event_date_end: str) -> dict:
        ...

    def get_attenders_age(self, season: str, event_date_start: str, event_date_end: str) -> pd.DataFrame:
        ...

    def get_attenders_distance(self, season: str, event_date_start: str, event_date_end: str) -> pd.DataFrame:
        ...

    def get_attenders_gender(self, season: str, event_date_start: str, event_date_end: str) -> pd.DataFrame:
        ...

    def get_attenders_outside_uk(self, season: str, event_date_start: str, event_date_end: str) -> pd.DataFrame:
        ...

    def get_one_off_ticket_attenders(self, season: str, event_date_start: str, event_date_end: str) -> dict:
        ...


class MockBackend(BaseBackend):
    """Returns realistic synthetic data for development/demo purposes."""

    def query(self, sql: str) -> pd.DataFrame:
        return pd.DataFrame()

    def list_tables(self) -> list[dict[str, Any]]:
        return [
            {"catalog": CATALOG, "schema": SCHEMA, "table": t, "status": "mock"}
            for t in ALL_TABLES
        ]

    def get_matchday_kpis(self, season="25/26", event_date_start="2025-08-01", event_date_end="2026-06-30") -> dict:
        return {
            "attenders": 1_277_120,
            "attendance_pct": 86.8,
            "tickets_sold": 1_470_678,
            "ticketing_revenue": 69_475_212,
            "unique_buyers": 102_460,
        }

    def get_attenders_age(self, season="25/26", event_date_start="2025-08-01", event_date_end="2026-06-30") -> pd.DataFrame:
        return pd.DataFrame({
            "age_band": ["17 and Under", "18-24", "25-34", "35-44", "45-54", "55-64", "65 and Over"],
            "percentage": [8, 11, 18, 18, 14, 14, 21],
        })

    def get_attenders_distance(self, season="25/26", event_date_start="2025-08-01", event_date_end="2026-06-30") -> pd.DataFrame:
        return pd.DataFrame({
            "distance_band": ["0-10", "11-25", "26-50", "51-100", "Over 100"],
            "percentage": [53, 14, 10, 8, 17],
        })

    def get_attenders_gender(self, season="25/26", event_date_start="2025-08-01", event_date_end="2026-06-30") -> pd.DataFrame:
        return pd.DataFrame({
            "gender": ["Male", "Female"],
            "percentage": [83, 17],
        })

    def get_attenders_outside_uk(self, season="25/26", event_date_start="2025-08-01", event_date_end="2026-06-30") -> pd.DataFrame:
        return pd.DataFrame({
            "country": ["Netherlands", "Ireland", "United States", "Italy", "Turkey"],
            "percentage": [18, 17, 10, 4, 4],
        })

    def get_one_off_ticket_attenders(self, season="25/26", event_date_start="2025-08-01", event_date_end="2026-06-30") -> dict:
        return {
            "total": 664_200,
            "max_range": 1_300_000,
            "first_timer_pct": 6.7,
            "avg_ticket_cost": 47,
        }

    def get_fixtures(self, season="25/26") -> pd.DataFrame:
        return pd.DataFrame({
            "fixture_id": [f"FIX-{i}" for i in range(1, 20)],
            "season": ["25/26"] * 19,
            "competition": ["Premier League"] * 19,
            "match_date": [date(2025, 8, 17) + timedelta(weeks=i) for i in range(19)],
            "home_team": ["Manchester City"] * 19,
            "away_team": [
                "Chelsea", "Ipswich Town", "Brentford", "Arsenal", "Newcastle",
                "Wolves", "Southampton", "Brighton", "Tottenham", "Bournemouth",
                "Nottm Forest", "Crystal Palace", "Man United", "West Ham",
                "Everton", "Leicester", "Aston Villa", "Liverpool", "Fulham"
            ],
        })

    def get_zendesk_summary(self) -> pd.DataFrame:
        categories = ["Ticketing", "Membership", "Retail", "Stadium", "City+", "General"]
        return pd.DataFrame({
            "category": categories,
            "ticket_count": [random.randint(200, 1500) for _ in categories],
            "avg_resolution_hours": [round(random.uniform(4, 48), 1) for _ in categories],
            "satisfaction_pct": [round(random.uniform(70, 95), 1) for _ in categories],
        })

    def get_retail_summary(self, season="25/26") -> dict:
        return {
            "total_revenue": 12_850_000,
            "total_transactions": 285_000,
            "avg_basket_size": 45.10,
            "top_category": "Replica Kits",
        }

    def get_membership_summary(self, season="25/26") -> dict:
        return {
            "total_members": 48_500,
            "new_members": 8_200,
            "renewal_rate": 82.5,
            "revenue": 3_450_000,
        }

    def get_engagement_summary(self) -> dict:
        return {
            "total_engagements": 5_200_000,
            "unique_fans_engaged": 320_000,
            "top_channel": "Email",
            "avg_engagements_per_fan": 16.25,
        }

    def get_tour_summary(self) -> dict:
        return {
            "total_tours": 85_000,
            "revenue": 2_100_000,
            "avg_group_size": 3.2,
            "satisfaction_pct": 92.4,
        }

    def get_facilities_kpis(self) -> dict:
        return {
            "capacity_utilization": 86.8,
            "avg_dwell_time_mins": 142,
            "food_bev_revenue": 8_500_000,
            "incidents_reported": 127,
        }


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
        return [
            {"catalog": CATALOG, "schema": SCHEMA, "table": row["tableName"], "status": "live"}
            for _, row in df.iterrows()
        ]

    def get_matchday_kpis(self, season="25/26", event_date_start="2025-08-01", event_date_end="2026-06-30") -> dict:
        sql = f"""
        SELECT
            COUNT(DISTINCT t.fan_id) AS attenders,
            COUNT(*) AS tickets_sold,
            SUM(t.ticket_price * t.quantity) AS ticketing_revenue,
            COUNT(DISTINCT CASE WHEN t.is_one_off THEN t.fan_id END) AS unique_buyers
        FROM {self._fqn('out_fact_ticketing_transactions')} t
        JOIN {self._fqn('out_dim_fixtures')} f ON t.fixture_id = f.fixture_id
        WHERE t.season = '{season}'
          AND f.match_date BETWEEN '{event_date_start}' AND '{event_date_end}'
        """
        df = self.query(sql)
        row = df.iloc[0]

        cap_sql = f"""
        SELECT COUNT(DISTINCT f.fixture_id) AS match_count
        FROM {self._fqn('out_dim_fixtures')} f
        WHERE f.season = '{season}'
          AND f.match_date BETWEEN '{event_date_start}' AND '{event_date_end}'
        """
        cap_df = self.query(cap_sql)
        match_count = cap_df.iloc[0]["match_count"] if len(cap_df) > 0 else 1
        stadium_capacity = 53_400
        attendance_pct = round(
            (row["attenders"] / (match_count * stadium_capacity)) * 100, 1
        ) if match_count > 0 else 0

        return {
            "attenders": int(row["attenders"]),
            "attendance_pct": attendance_pct,
            "tickets_sold": int(row["tickets_sold"]),
            "ticketing_revenue": float(row["ticketing_revenue"] or 0),
            "unique_buyers": int(row["unique_buyers"]),
        }

    def get_attenders_age(self, season="25/26", event_date_start="2025-08-01", event_date_end="2026-06-30") -> pd.DataFrame:
        sql = f"""
        SELECT
            d.age_band,
            ROUND(COUNT(DISTINCT t.fan_id) * 100.0 /
                  (SELECT COUNT(DISTINCT fan_id) FROM {self._fqn('out_fact_ticketing_transactions')}
                   WHERE season = '{season}'), 0) AS percentage
        FROM {self._fqn('out_fact_ticketing_transactions')} t
        JOIN {self._fqn('out_dim_fans')} d ON t.fan_id = d.fan_id
        JOIN {self._fqn('out_dim_fixtures')} f ON t.fixture_id = f.fixture_id
        WHERE t.season = '{season}'
          AND f.match_date BETWEEN '{event_date_start}' AND '{event_date_end}'
          AND d.age_band IS NOT NULL
        GROUP BY d.age_band
        ORDER BY d.age_band
        """
        return self.query(sql)

    def get_attenders_distance(self, season="25/26", event_date_start="2025-08-01", event_date_end="2026-06-30") -> pd.DataFrame:
        sql = f"""
        SELECT
            d.distance_band,
            ROUND(COUNT(DISTINCT t.fan_id) * 100.0 /
                  (SELECT COUNT(DISTINCT fan_id) FROM {self._fqn('out_fact_ticketing_transactions')}
                   WHERE season = '{season}'), 0) AS percentage
        FROM {self._fqn('out_fact_ticketing_transactions')} t
        JOIN {self._fqn('out_dim_fans')} d ON t.fan_id = d.fan_id
        JOIN {self._fqn('out_dim_fixtures')} f ON t.fixture_id = f.fixture_id
        WHERE t.season = '{season}'
          AND f.match_date BETWEEN '{event_date_start}' AND '{event_date_end}'
          AND d.distance_band IS NOT NULL
        GROUP BY d.distance_band
        ORDER BY d.distance_band
        """
        return self.query(sql)

    def get_attenders_gender(self, season="25/26", event_date_start="2025-08-01", event_date_end="2026-06-30") -> pd.DataFrame:
        sql = f"""
        SELECT
            d.gender,
            ROUND(COUNT(DISTINCT t.fan_id) * 100.0 /
                  (SELECT COUNT(DISTINCT fan_id) FROM {self._fqn('out_fact_ticketing_transactions')}
                   WHERE season = '{season}'), 0) AS percentage
        FROM {self._fqn('out_fact_ticketing_transactions')} t
        JOIN {self._fqn('out_dim_fans')} d ON t.fan_id = d.fan_id
        JOIN {self._fqn('out_dim_fixtures')} f ON t.fixture_id = f.fixture_id
        WHERE t.season = '{season}'
          AND f.match_date BETWEEN '{event_date_start}' AND '{event_date_end}'
          AND d.gender IS NOT NULL
        GROUP BY d.gender
        """
        return self.query(sql)

    def get_attenders_outside_uk(self, season="25/26", event_date_start="2025-08-01", event_date_end="2026-06-30") -> pd.DataFrame:
        sql = f"""
        SELECT
            d.country,
            ROUND(COUNT(DISTINCT t.fan_id) * 100.0 /
                  (SELECT COUNT(DISTINCT fan_id) FROM {self._fqn('out_fact_ticketing_transactions')}
                   WHERE season = '{season}'
                     AND fan_id IN (SELECT fan_id FROM {self._fqn('out_dim_fans')} WHERE country != 'United Kingdom')), 0) AS percentage
        FROM {self._fqn('out_fact_ticketing_transactions')} t
        JOIN {self._fqn('out_dim_fans')} d ON t.fan_id = d.fan_id
        JOIN {self._fqn('out_dim_fixtures')} f ON t.fixture_id = f.fixture_id
        WHERE t.season = '{season}'
          AND f.match_date BETWEEN '{event_date_start}' AND '{event_date_end}'
          AND d.country != 'United Kingdom'
          AND d.country IS NOT NULL
        GROUP BY d.country
        ORDER BY COUNT(DISTINCT t.fan_id) DESC
        LIMIT 5
        """
        return self.query(sql)

    def get_one_off_ticket_attenders(self, season="25/26", event_date_start="2025-08-01", event_date_end="2026-06-30") -> dict:
        sql = f"""
        SELECT
            COUNT(DISTINCT t.fan_id) AS total,
            ROUND(
                COUNT(DISTINCT CASE WHEN d.first_timer THEN t.fan_id END) * 100.0 /
                NULLIF(COUNT(DISTINCT t.fan_id), 0), 1
            ) AS first_timer_pct,
            ROUND(AVG(t.ticket_price), 0) AS avg_ticket_cost
        FROM {self._fqn('out_fact_ticketing_transactions')} t
        JOIN {self._fqn('out_dim_fans')} d ON t.fan_id = d.fan_id
        JOIN {self._fqn('out_dim_fixtures')} f ON t.fixture_id = f.fixture_id
        WHERE t.season = '{season}'
          AND t.is_one_off = true
          AND f.match_date BETWEEN '{event_date_start}' AND '{event_date_end}'
        """
        df = self.query(sql)
        row = df.iloc[0]

        total_sql = f"SELECT COUNT(DISTINCT fan_id) AS max_range FROM {self._fqn('out_fact_ticketing_transactions')} WHERE season = '{season}'"
        total_df = self.query(total_sql)

        return {
            "total": int(row["total"]),
            "max_range": int(total_df.iloc[0]["max_range"]) if len(total_df) > 0 else 0,
            "first_timer_pct": float(row["first_timer_pct"] or 0),
            "avg_ticket_cost": int(row["avg_ticket_cost"] or 0),
        }

    def get_fixtures(self, season="25/26") -> pd.DataFrame:
        return self.query(f"""
            SELECT * FROM {self._fqn('out_dim_fixtures')}
            WHERE season = '{season}'
            ORDER BY match_date
        """)

    def get_zendesk_summary(self) -> pd.DataFrame:
        return self.query(f"""
            SELECT
                c.category_name AS category,
                COUNT(*) AS ticket_count,
                ROUND(AVG(DATEDIFF(t.resolved_date, t.created_date) * 24), 1) AS avg_resolution_hours,
                ROUND(
                    COUNT(CASE WHEN t.satisfaction_rating = 'good' THEN 1 END) * 100.0 /
                    NULLIF(COUNT(CASE WHEN t.satisfaction_rating IS NOT NULL THEN 1 END), 0), 1
                ) AS satisfaction_pct
            FROM {self._fqn('out_fact_zendesk_tickets')} t
            JOIN {self._fqn('out_fact_zendesk_category')} c ON t.category = c.category_id
            GROUP BY c.category_name
        """)

    def get_retail_summary(self, season="25/26") -> dict:
        df = self.query(f"""
            SELECT
                SUM(total_amount) AS total_revenue,
                COUNT(*) AS total_transactions,
                ROUND(AVG(total_amount), 2) AS avg_basket_size
            FROM {self._fqn('out_fact_retail_transactions')}
            WHERE season = '{season}'
        """)
        row = df.iloc[0]

        top = self.query(f"""
            SELECT p.category, SUM(r.total_amount) AS rev
            FROM {self._fqn('out_fact_retail_transactions')} r
            JOIN {self._fqn('out_dim_retail_products')} p ON r.product_id = p.product_id
            WHERE r.season = '{season}'
            GROUP BY p.category
            ORDER BY rev DESC LIMIT 1
        """)

        return {
            "total_revenue": float(row["total_revenue"] or 0),
            "total_transactions": int(row["total_transactions"] or 0),
            "avg_basket_size": float(row["avg_basket_size"] or 0),
            "top_category": top.iloc[0]["category"] if len(top) > 0 else "N/A",
        }

    def get_membership_summary(self, season="25/26") -> dict:
        df = self.query(f"""
            SELECT
                COUNT(DISTINCT fan_id) AS total_members,
                SUM(amount) AS revenue
            FROM {self._fqn('out_fact_membership_transactions')}
            WHERE season = '{season}'
        """)
        row = df.iloc[0]
        return {
            "total_members": int(row["total_members"] or 0),
            "new_members": 0,
            "renewal_rate": 0,
            "revenue": float(row["revenue"] or 0),
        }

    def get_engagement_summary(self) -> dict:
        df = self.query(f"""
            SELECT
                COUNT(*) AS total_engagements,
                COUNT(DISTINCT fan_id) AS unique_fans_engaged
            FROM {self._fqn('out_fact_engagements')}
        """)
        row = df.iloc[0]
        total = int(row["total_engagements"] or 0)
        unique = int(row["unique_fans_engaged"] or 1)
        return {
            "total_engagements": total,
            "unique_fans_engaged": unique,
            "top_channel": "Email",
            "avg_engagements_per_fan": round(total / max(unique, 1), 2),
        }

    def get_tour_summary(self) -> dict:
        df = self.query(f"""
            SELECT
                COUNT(DISTINCT fan_id) AS total_tours,
                SUM(amount) AS revenue,
                ROUND(AVG(quantity), 1) AS avg_group_size
            FROM {self._fqn('out_fact_tour_transactions')}
        """)
        row = df.iloc[0]
        return {
            "total_tours": int(row["total_tours"] or 0),
            "revenue": float(row["revenue"] or 0),
            "avg_group_size": float(row["avg_group_size"] or 0),
            "satisfaction_pct": 0,
        }

    def get_facilities_kpis(self) -> dict:
        return {
            "capacity_utilization": 0,
            "avg_dwell_time_mins": 0,
            "food_bev_revenue": 0,
            "incidents_reported": 0,
        }


def get_backend() -> BaseBackend:
    if USE_MOCK:
        return MockBackend()
    return RealBackend()
