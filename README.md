# ⚽ Man City Ticketing Intelligence Platform

A **bespoke ticketing analytics application** built on AI-ready pipelines,
packaged as a **Databricks Asset Bundle** for one-command deployment.

![Dash](https://img.shields.io/badge/Dash-4.0-blue)
![Plotly](https://img.shields.io/badge/Plotly-5.x-blueviolet)
![Databricks](https://img.shields.io/badge/Databricks-App-orange)

---

## 🎯 What's Inside

| Page | Description |
|---|---|
| **Command Center** | 12 KPIs (revenue, attendance, sell-through, digital %), revenue trend, competition split, sale channels, demographics |
| **Revenue Analytics** | Revenue by match (28 fixtures), price-band distribution, competition breakdown |
| **Seat Intelligence** | Section-level occupancy heat bars, capacity-vs-revenue scatter, full section table |
| **Fan Segments** | Buyer segment treemap (6 tiers w/ retention rates), distance, gender, international fans |
| **Match Explorer** | All-match table with sell-through bars, avg price, attendance |
| **Pipeline Health** | AI-readiness dashboard – data freshness, quality scores, row counts for every Unity Catalog table |
| **Support Analytics** | Zendesk category breakdown with resolution times and satisfaction |

---

## 📂 Project Structure

```
mancity-footballhub/
├── databricks.yml              # Asset Bundle config (dev / prod)
├── resources/
│   └── fan_intelligence_hub.app.yml   # App resource definition
├── app/
│   ├── app.py                  # Dash 4.0 multi-page UI (7 pages)
│   ├── backend.py              # Mock + Real Databricks SQL backend
│   ├── models.py               # Pydantic models for 17 tables
│   ├── app.yaml                # Databricks App config (env vars)
│   ├── requirements.txt        # Python dependencies
│   └── assets/                 # Logos & images
│       ├── mancity-crest.png
│       ├── databricks-logo.png
│       └── etihad-stadium.png
└── README.md
```

---

## 🚀 Quick Start (Local)

```bash
cd app
pip install -r requirements.txt
USE_MOCK_BACKEND=true python app.py
# Open http://localhost:8080
```

The app ships with **comprehensive mock data** that runs without any Databricks connection.

---

## ☁️ Deploy to Databricks

### Prerequisites

1. **Databricks CLI** ≥ 0.230 with a configured profile  
2. **Unity Catalog tables** — the 17 `out_*` / `work_*` tables loaded into your catalog  
3. **SQL Warehouse** — serverless or pro, accessible by the app service principal  

### One-Command Deploy

```bash
# Dev environment (personal prefix, development mode)
databricks bundle deploy -t dev

# Production
databricks bundle deploy -t prod
```

### Configure Your Catalog

Edit `databricks.yml` variables:

```yaml
variables:
  catalog:
    default: "your_catalog"
  schema:
    default: "your_schema"
  warehouse_id:
    lookup:
      warehouse: "Your Warehouse Name"
```

These flow into `app.yaml` as environment variables the app reads at runtime.

### Switch to Real Data

In `app.yaml`, set:
```yaml
- name: USE_MOCK_BACKEND
  value: "false"
```

The app will query your Unity Catalog tables via the SQL Warehouse.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────┐
│               Dash 4.0 Frontend                  │
│  Command Center │ Revenue │ Seats │ Fans │ ...   │
├──────────────────────────────────────────────────┤
│             backend.py (Toggle)                  │
│     USE_MOCK_BACKEND=true  │  =false             │
│     ↓ MockBackend          │  ↓ RealBackend      │
│     Synthetic data         │  SQL Warehouse      │
│     (no connection)        │  via Unity Catalog   │
└──────────────────────────────────────────────────┘
```

### Required Tables

| # | Table | Purpose |
|---|---|---|
| 1 | `out_dim_fans` | Fan demographics (age, distance, gender, country) |
| 2 | `out_dim_fixtures` | Match schedule, competition, venue |
| 3 | `out_dim_retail_products` | Merchandise catalog |
| 4 | `out_dim_tour_events` | Stadium tour events |
| 5 | `out_fact_cityplus_transactions` | City+ subscription data |
| 6 | `out_fact_engagement_group` | Engagement group scores |
| 7 | `out_fact_engagements` | Individual engagement events |
| 8 | `out_fact_membership_transactions` | Membership purchases |
| 9 | `out_fact_retail_discounts` | Retail discount usage |
| 10 | `out_fact_retail_transactions` | Retail sales |
| 11 | `out_fact_ticketing_transactions` | **Core** — all ticket sales |
| 12 | `out_fact_tour_transactions` | Tour ticket sales |
| 13 | `out_fact_zendesk_category` | Support ticket categories |
| 14 | `out_fact_zendesk_tickets` | Support tickets |
| 15 | `work_membership_id_table` | Membership ID mapping |
| 16 | `work_surrogate_id_table` | Surrogate key mapping |
| 17 | `work_transtable_reduced` | Reduced transaction table |

---

## 🔧 Environment Variables

| Variable | Description | Default |
|---|---|---|
| `USE_MOCK_BACKEND` | `true` = synthetic data, `false` = live SQL | `true` |
| `DATABRICKS_WAREHOUSE_ID` | SQL Warehouse ID | *(from app.yaml)* |
| `DATABRICKS_CATALOG` | Unity Catalog name | `algatty_manchester_usr_gp` |
| `DATABRICKS_SCHEMA` | Schema within catalog | `default` |

---

## 🧹 Cleanup

```bash
databricks bundle destroy -t dev
```

---

## 📜 License

Internal use — Manchester City FC / Databricks.
