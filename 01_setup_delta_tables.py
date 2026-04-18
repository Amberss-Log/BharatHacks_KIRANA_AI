# Databricks notebook source
spark.sql("""
CREATE TABLE IF NOT EXISTS workspace.default.shop_priors (
    shop_id                  STRING,
    matched_store_ids        STRING,
    avg_qty_prior            DOUBLE,
    avg_amt_prior            DOUBLE,
    avg_amt_prior_inr        DOUBLE,
    confidence_score         DOUBLE,
    seasonality_pattern      STRING,
    flag                     STRING,
    created_at               TIMESTAMP
)
USING DELTA
""")
print("✅ shop_priors table created")

# COMMAND ----------

# ─── CELL 1: Create all Delta tables ───────────────────
catalog = "workspace"
schema  = "default"

spark.sql(f"USE CATALOG {catalog}")
spark.sql(f"USE SCHEMA {schema}")

# 1. Shop Profile
spark.sql("""
CREATE TABLE IF NOT EXISTS workspace.default.shop_profiles (
    shop_id        STRING,
    shop_name      STRING,
    owner_name     STRING,
    location       STRING,
    village        STRING,
    district       STRING,
    state          STRING,
    shop_type      STRING,
    language       STRING,
    lead_time_min  INT,
    lead_time_max  INT,
    created_at     TIMESTAMP
)
USING DELTA
""")

# 2. Sales Log (manual daily entries)
spark.sql("""
CREATE TABLE IF NOT EXISTS workspace.default.sales_log (
    log_id         STRING,
    shop_id        STRING,
    date           DATE,
    product_name   STRING,
    category       STRING,
    qty_sold       DOUBLE,
    price_per_unit DOUBLE,
    total_amount   DOUBLE,
    logged_at      TIMESTAMP
)
USING DELTA
""")

# 3. Inventory (current stock levels)
spark.sql("""
CREATE TABLE IF NOT EXISTS workspace.default.shop_inventory (
    shop_id        STRING,
    product_name   STRING,
    category       STRING,
    current_stock  DOUBLE,
    unit           STRING,
    reorder_point  DOUBLE,
    eoq            DOUBLE,
    safety_stock   DOUBLE,
    last_updated   TIMESTAMP
)
USING DELTA
""")

# 4. Daily Metrics (IE calculations)
spark.sql("""
CREATE TABLE IF NOT EXISTS workspace.default.daily_metrics (
    shop_id           STRING,
    date              DATE,
    total_revenue     DOUBLE,
    total_units       INT,
    products_moved    INT,
    avg_basket_value  DOUBLE,
    top_category      STRING,
    dos_avg           DOUBLE,
    stockout_risk_count INT,
    calculated_at     TIMESTAMP
)
USING DELTA
""")

# 5. Forecasts Log
spark.sql("""
CREATE TABLE IF NOT EXISTS workspace.default.forecasts_log (
    shop_id          STRING,
    forecast_date    DATE,
    product_name     STRING,
    category         STRING,
    forecast_1d_qty  DOUBLE,
    forecast_7d_qty  DOUBLE,
    forecast_30d_qty DOUBLE,
    forecast_1d_amt  DOUBLE,
    forecast_7d_amt  DOUBLE,
    forecast_30d_amt DOUBLE,
    method           STRING,
    created_at       TIMESTAMP
)
USING DELTA
""")

# 6. Reorder Alerts
spark.sql("""
CREATE TABLE IF NOT EXISTS workspace.default.reorder_alerts (
    shop_id        STRING,
    alert_date     DATE,
    product_name   STRING,
    category       STRING,
    current_stock  DOUBLE,
    days_remaining DOUBLE,
    reorder_qty    DOUBLE,
    rop            DOUBLE,
    urgency        STRING,
    resolved       BOOLEAN,
    created_at     TIMESTAMP
)
USING DELTA
""")

# 7. Weekly Stocking Plan
spark.sql("""
CREATE TABLE IF NOT EXISTS workspace.default.weekly_stocking_plan (
    shop_id        STRING,
    week_start     DATE,
    product_name   STRING,
    category       STRING,
    recommended_qty DOUBLE,
    estimated_cost  DOUBLE,
    priority        STRING,
    created_at      TIMESTAMP
)
USING DELTA
""")

print("✅ All Delta tables created successfully")

# COMMAND ----------

# ─── CELL 2: Insert Sharma ji's shop profile ───────────
from pyspark.sql import Row
from datetime import datetime

shop_row = Row(
    shop_id       = "SHARMA_SIMROL_001",
    shop_name     = "Sharma Ji Kirana Store",
    owner_name    = "Sharma Ji",
    location      = "Simrol, Indore, MP",
    village       = "Simrol",
    district      = "Indore",
    state         = "Madhya Pradesh",
    shop_type     = "kirana",
    language      = "hi",
    lead_time_min = 1,
    lead_time_max = 4,
    created_at    = datetime.now()
)

spark.createDataFrame([shop_row]).write \
    .format("delta") \
    .mode("append") \
    .saveAsTable("workspace.default.shop_profiles")

print("✅ Sharma Ji's shop profile created")