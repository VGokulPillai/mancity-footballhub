# Man City Fan Intelligence Hub

A pixel-accurate replica of the Power BI Fan Intelligence Hub matchday dashboard, rebuilt as a **Databricks App** with **Dash + Plotly** and packaged as a **Databricks Asset Bundle (DABs)** for one-command deployment.

![Fan Intelligence Hub](app/assets/etihad-stadium.png)

---

## Architecture

```
mancity-footballhub/
├── databricks.yml                    # DABs config (dev + prod targets)
├── resources/
│   └── fan_intelligence_hub.app.yml  # Databricks App resource definition
├── app/
│   ├── app.py                        # Dash application (pixel-match UI)
│   ├── backend.py                    # Data layer (mock + real backends)
│   ├── models.py                     # Pydantic models for all 17 tables
│   ├── app.yaml                      # Databricks Apps runtime config
│   ├── requirements.txt              # Python dependencies
│   └── assets/                       # Man City crest, Databricks logo, stadium
└── README.md
```

---

## Data Tables (17 Unity Catalog tables)

| Table | Type | Description |
|-------|------|-------------|
| `out_dim_fans` | Dimension | Fan demographics, location, age bands, membership |
| `out_dim_fixtures` | Dimension | Match schedule, competitions, results, venues |
| `out_dim_retail_products` | Dimension | Product catalog for merchandise |
| `out_dim_tour_events` | Dimension | Stadium tour event listings |
| `out_fact_ticketing_transactions` | Fact | Ticket sales, pricing, seat allocation |
| `out_fact_engagements` | Fact | Fan engagement across channels |
| `out_fact_engagement_group` | Fact | Engagement group summaries |
| `out_fact_membership_transactions` | Fact | Membership purchases and renewals |
| `out_fact_retail_transactions` | Fact | Merchandise sales |
| `out_fact_retail_discounts` | Fact | Discount campaigns |
| `out_fact_cityplus_transactions` | Fact | City+ streaming subscriptions |
| `out_fact_tour_transactions` | Fact | Stadium tour bookings |
| `out_fact_zendesk_tickets` | Fact | Customer support tickets |
| `out_fact_zendesk_category` | Fact | Support ticket categories |
| `work_membership_id_table` | Work | Membership ID mapping |
| `work_surrogate_id_table` | Work | Surrogate key mapping |
| `work_transtable_reduced` | Work | Reduced transaction staging |

---

## Dashboard Pages

| Page | Description |
|------|-------------|
| **Matchday** | KPIs (attenders, attendance %, tickets sold, revenue, unique buyers) + age/distance/gender/outside UK/one-off ticket charts with full filter panel |
| **Zendesk** | Support ticket analytics by category with resolution and satisfaction |
| **Merchandise** | Retail revenue, basket size, top product categories |
| **Facilities KPIs** | Capacity utilization, dwell time, F&B revenue |
| **Product** | Membership, engagement, and stadium tour analytics |
| **Data Tables** | View all 17 Unity Catalog tables and their connection status |

---

## Quick Start — Local Development

```bash
cd app
pip install -r requirements.txt
python app.py
# Opens at http://localhost:8080 with mock data
```

Mock mode is enabled by default (`USE_MOCK_BACKEND=true`) so the app runs without any Databricks connection. The mock data matches the exact values from the Power BI dashboard screenshot.

---

## Configuration

Set these in `app/app.yaml` (for Databricks deployment) or as environment variables (for local):

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_MOCK_BACKEND` | `true` | Set to `false` to query real Databricks tables |
| `DATABRICKS_CATALOG` | `algatty_manchester_usr_gp` | Unity Catalog name containing the tables |
| `DATABRICKS_SCHEMA` | `default` | Schema containing the tables |
| `DATABRICKS_WAREHOUSE_ID` | *(from app resource)* | SQL Warehouse ID for query execution |

---

## Deploy to Databricks

### Prerequisites

1. **Databricks CLI** v0.239.0 or later — [install guide](https://docs.databricks.com/dev-tools/cli/install)
2. **Authenticated profile** — run `databricks auth login` for your workspace
3. **SQL Warehouse** — with access to the Unity Catalog tables above
4. **Tables loaded** — all 17 `out_*` and `work_*` tables must exist in the target catalog/schema

### Step-by-step deployment

```bash
# 1. Clone the repo
git clone https://github.com/VGokulPillai/mancity-footballhub.git
cd mancity-footballhub

# 2. Authenticate to your Databricks workspace
databricks auth login --host https://<your-workspace>.azuredatabricks.net --profile my-workspace

# 3. Update databricks.yml with your profile and catalog/schema
#    Edit targets → prod → workspace → profile
#    Edit targets → prod → variables → catalog / schema

# 4. Update app/app.yaml with your catalog, schema, and warehouse
#    Edit env → DATABRICKS_CATALOG → value
#    Edit env → DATABRICKS_SCHEMA → value
#    Set USE_MOCK_BACKEND → "false"

# 5. Validate the bundle
databricks bundle validate

# 6. Deploy
databricks bundle deploy -t prod

# 7. Start the app
databricks bundle run fan_intelligence_hub -t prod

# 8. Check logs if needed
databricks apps logs mancity-fan-hub-prod --profile my-workspace
```

### Quick deploy (dev mode)

```bash
# Uses the default dev target with your local profile
databricks bundle deploy
databricks bundle run fan_intelligence_hub
```

---

## Client Deployment Guide

To deploy this to a **different Databricks workspace** (e.g. for a client):

### 1. Update `databricks.yml`

```yaml
targets:
  prod:
    mode: production
    workspace:
      profile: client-workspace    # <- client's Databricks CLI profile
    variables:
      catalog: "client_catalog"    # <- their Unity Catalog name
      schema: "client_schema"      # <- their schema name
```

### 2. Update `app/app.yaml`

```yaml
env:
  - name: USE_MOCK_BACKEND
    value: "false"                 # <- connect to real tables
  - name: DATABRICKS_CATALOG
    value: "client_catalog"        # <- match databricks.yml
  - name: DATABRICKS_SCHEMA
    value: "client_schema"         # <- match databricks.yml
```

### 3. Authenticate and deploy

```bash
# Authenticate to client workspace
databricks auth login --host https://<client-workspace>.azuredatabricks.net --profile client-workspace

# Validate
databricks bundle validate -t prod

# Deploy
databricks bundle deploy -t prod

# Start the app
databricks bundle run fan_intelligence_hub -t prod
```

### 4. Verify

```bash
# Check deployment logs
databricks apps logs mancity-fan-hub-prod --profile client-workspace

# The app URL will be:
# https://mancity-fan-hub-prod-<workspace-id>.azuredatabricksapps.com
```

---

## Table Requirements

For the real backend to work, the client workspace must have:

1. A **Unity Catalog** with all 17 tables (matching the names in the Data Tables section)
2. A running **SQL Warehouse** (serverless recommended)
3. The warehouse's **service principal** must have `SELECT` on all tables
4. Add the warehouse as an app resource in the Databricks UI after deployment

---

## Cleanup

```bash
# Remove dev deployment
databricks bundle destroy -t dev

# Remove prod deployment
databricks bundle destroy -t prod --auto-approve
```

---

## Technology Stack

- **Frontend**: Dash 2.x + Plotly + dash-bootstrap-components (Darkly theme)
- **Backend**: Python with mock/real toggle pattern
- **Data**: Databricks Unity Catalog via SQL Warehouse
- **Deployment**: Databricks Asset Bundles (DABs)
- **Auth**: Databricks SDK `Config()` auto-detection (service principal)
