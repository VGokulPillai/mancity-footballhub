# Man City Fan Intelligence Hub

A comprehensive matchday analytics dashboard for Manchester City FC, built on **Databricks** with **Dash** and deployable via **Databricks Asset Bundles (DABs)**.

## Architecture

```
mancity-footballhub/
├── databricks.yml              # DABs main config (multi-env targets)
├── resources/
│   └── fan_intelligence_hub.app.yml  # App resource definition
├── app/
│   ├── app.py                  # Dash application (main entry point)
│   ├── backend.py              # Data access layer (mock + real backends)
│   ├── models.py               # Pydantic models for all 17 tables
│   ├── app.yaml                # Databricks Apps runtime config
│   ├── requirements.txt        # Python dependencies
│   └── assets/                 # Static images (crest, logos, stadium)
└── sql/                        # SQL reference files
```

## Data Tables

The app reads from **17 Unity Catalog tables**:

| Table | Type | Description |
|-------|------|-------------|
| `out_dim_fans` | Dimension | Fan demographics, location, membership |
| `out_dim_fixtures` | Dimension | Match schedule, results, venues |
| `out_dim_retail_products` | Dimension | Product catalog for merchandise |
| `out_dim_tour_events` | Dimension | Stadium tour events |
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

## Dashboard Pages

- **Home** — Overview with navigation cards to all sections
- **Matchday** — Attendance KPIs, age/distance/gender demographics, one-off ticket analysis
- **Zendesk** — Support ticket analytics and satisfaction metrics
- **Merchandise** — Retail revenue, basket size, top categories
- **Facilities KPIs** — Capacity utilization, dwell time, F&B revenue
- **Product** — Membership, engagement, and stadium tour analytics
- **Data Tables** — View all 17 tables and their connection status

## Quick Start (Local Development)

```bash
cd app
pip install -r requirements.txt
# Mock backend is enabled by default
python app.py
# Open http://localhost:8080
```

## Configuration

Set these environment variables (or configure in `app.yaml`):

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_MOCK_BACKEND` | `true` | Set to `false` to query real Databricks tables |
| `DATABRICKS_CATALOG` | `algatty_manchester_usr_gp` | Unity Catalog name |
| `DATABRICKS_SCHEMA` | `default` | Schema containing the tables |
| `DATABRICKS_WAREHOUSE_ID` | *(required for real backend)* | SQL Warehouse ID |

## Deploy to Databricks

### Prerequisites

1. [Databricks CLI](https://docs.databricks.com/dev-tools/cli/install) v0.239.0+
2. Authenticated profile: `databricks auth login --host <workspace-url> --profile <profile>`
3. SQL Warehouse with access to the Unity Catalog tables

### Deploy with DABs

```bash
# Validate the bundle
databricks bundle validate

# Deploy to dev
databricks bundle deploy

# Start the app
databricks bundle run fan_intelligence_hub

# Deploy to production
databricks bundle deploy -t prod
databricks bundle run fan_intelligence_hub -t prod
```

### Client Deployment

To deploy to a **different workspace** (e.g., for your client):

1. **Update `databricks.yml`** — change the workspace profile and variable values:
   ```yaml
   targets:
     prod:
       workspace:
         profile: client-workspace-profile
       variables:
         catalog: "client_catalog_name"
         schema: "client_schema_name"
   ```

2. **Update `app/app.yaml`** — set the correct catalog and schema:
   ```yaml
   env:
     - name: DATABRICKS_CATALOG
       value: "client_catalog_name"
     - name: DATABRICKS_SCHEMA
       value: "client_schema_name"
   ```

3. **Authenticate and deploy**:
   ```bash
   databricks auth login --host <client-workspace-url> --profile client-workspace-profile
   databricks bundle deploy -t prod
   databricks bundle run fan_intelligence_hub -t prod
   ```

## Cleanup

```bash
databricks bundle destroy -t dev
```
