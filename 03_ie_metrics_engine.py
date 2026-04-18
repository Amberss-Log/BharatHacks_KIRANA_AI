# Databricks notebook source
import json

def bayesian_forecast(shop_id: str,
                      prior: dict,
                      local_sales_history: list) -> dict:
    """
    Blends RAG prior with real daily sales history.
    
    local_sales_history = list of actual daily revenue in INR
    e.g. [] on day 0, [9500] on day 1, [9500, 11200] on day 2, etc.
    
    Prior strength = 7 (prior counts as 7 days of virtual data)
    As real data grows, prior weight shrinks automatically.
    """
    INR            = 83.0
    prior_mean     = prior["avg_amt_prior"] * INR
    prior_strength = 7   # prior counts as this many days of data
    n              = len(local_sales_history)
    
    if n == 0:
        # Day 0 — no real data, use prior completely
        posterior_mean = prior_mean
        prior_weight   = 1.0
        data_weight    = 0.0
    else:
        real_mean    = float(np.mean(local_sales_history))
        prior_weight = prior_strength / (prior_strength + n)
        data_weight  = n              / (prior_strength + n)
        posterior_mean = (prior_weight * prior_mean) + (data_weight * real_mean)
    
    # Festival multiplier from seasonality pattern
    current_week = int(spark.sql(
        "SELECT WEEKOFYEAR(CURRENT_DATE()) AS w"
    ).collect()[0]["w"])
    
    seasonality         = prior.get("seasonality_pattern", [1.0] * 52)
    avg_season          = float(np.mean(seasonality))
    festival_multiplier = (
        seasonality[current_week - 1] / avg_season
        if avg_season > 0 else 1.0
    )
    
    adjusted_forecast = posterior_mean * festival_multiplier
    
    return {
        "shop_id":                     shop_id,
        "days_of_real_data":           n,
        "prior_weight":                round(prior_weight, 3),
        "data_weight":                 round(data_weight, 3),
        "posterior_daily_revenue_inr": round(posterior_mean, 2),
        "festival_multiplier":         round(festival_multiplier, 3),
        "adjusted_forecast_inr":       round(adjusted_forecast, 2),
        "current_week":                current_week,
        "source": "rag_prior" if n == 0 else f"bayesian_blend_{n}_days"
    }

print("Bayesian function defined.")

def load_shop_prior(shop_id):
    """Load RAG prior from Delta — saved at onboarding"""
    rows = spark.sql(f"""
        SELECT * FROM workspace.default.shop_priors
        WHERE shop_id = '{shop_id}'
        ORDER BY created_at DESC
        LIMIT 1
    """).collect()
    
    if not rows:
        # Fallback if RAG hasn't run yet
        return {
            "avg_amt_prior": 100.0,
            "avg_qty_prior": 5.0,
            "avg_amt_prior_inr": 8300.0,
            "seasonality_pattern": [1.0] * 52,
            "confidence_score": 0.0,
            "flag": "no_prior_found"
        }
    
    r = rows[0]
    return {
        "avg_amt_prior":       r["avg_amt_prior"],
        "avg_qty_prior":       r["avg_qty_prior"],
        "avg_amt_prior_inr":   r["avg_amt_prior_inr"],
        "seasonality_pattern": json.loads(r["seasonality_pattern"]),
        "confidence_score":    r["confidence_score"],
        "flag":                r["flag"]
    }

# Load it
shop_prior = load_shop_prior(SHOP_ID)
print(f"✅ Prior loaded — confidence: {shop_prior['confidence_score']}")
print(f"   RAG daily revenue prior: ₹{shop_prior['avg_amt_prior_inr']:,.0f}")

# ─── CELL 1: IE Constants ──────────────────────────────
SHOP_ID       = "SHARMA_SIMROL_001"
LEAD_TIME_MIN = 1   # days
LEAD_TIME_MAX = 4   # days
LEAD_TIME_AVG = 2.5 # average
Z_SCORE       = 1.65  # 95% service level
ORDERING_COST = 50    # ₹ per order (fixed cost)
HOLDING_RATE  = 0.20  # 20% of item value per year
WORKING_DAYS  = 365

print("✅ IE constants set")
print(f"   Lead Time: {LEAD_TIME_MIN}–{LEAD_TIME_MAX} days")
print(f"   Service Level: {Z_SCORE*100/1.65:.0f}%")
print(f"   Ordering Cost: ₹{ORDERING_COST}")

# COMMAND ----------

# ─── CELL 2: Load sales history ────────────────────────
from pyspark.sql import functions as F
from pyspark.sql.window import Window
import pandas as pd
import numpy as np

def load_sales_history(shop_id, days=30):
    df = spark.sql(f"""
        SELECT 
            date, product_name, category,
            SUM(qty_sold) as qty_sold,
            AVG(price_per_unit) as price_per_unit,
            SUM(total_amount) as total_amount
        FROM workspace.default.sales_log
        WHERE shop_id = '{shop_id}'
          AND date >= date_sub(current_date(), {days})
        GROUP BY date, product_name, category
        ORDER BY date, product_name
    """)
    return df.toPandas()

pdf = load_sales_history(SHOP_ID, days=30)
print(f"✅ Loaded {len(pdf)} rows | {pdf['product_name'].nunique()} products | {pdf['date'].nunique()} days")
pdf.head()

# COMMAND ----------

# ─── CELL 3: EWM Forecasting engine ────────────────────
def ewm_forecast(pdf, product_name, horizon_days):
    """
    Exponential Weighted Moving Average forecast
    horizon_days: 1, 7, or 30
    Returns: predicted total qty and amount for that horizon
    """
    prod_df = pdf[pdf["product_name"] == product_name].copy()
    prod_df = prod_df.sort_values("date")
    
    if len(prod_df) < 3:
        # Not enough data — use category average
        cat = prod_df["category"].iloc[0]
        cat_avg = pdf[pdf["category"] == cat]["qty_sold"].mean()
        return cat_avg * horizon_days, \
               cat_avg * prod_df["price_per_unit"].mean() * horizon_days
    
    # EWM — span=7 reacts to recent week strongly
    prod_df["ewm_qty"] = prod_df["qty_sold"].ewm(span=7, adjust=False).mean()
    prod_df["ewm_amt"] = prod_df["total_amount"].ewm(span=7, adjust=False).mean()
    
    daily_qty = prod_df["ewm_qty"].iloc[-1]
    daily_amt = prod_df["ewm_amt"].iloc[-1]
    
    return round(daily_qty * horizon_days, 2), \
           round(daily_amt * horizon_days, 2)

# Test
qty_1d, amt_1d = ewm_forecast(pdf, "Tata Salt 1kg", 1)
qty_7d, amt_7d = ewm_forecast(pdf, "Tata Salt 1kg", 7)
print(f"Tata Salt — Tomorrow: {qty_1d} units | 7 days: {qty_7d} units")

# COMMAND ----------

# ─── CELL 4: IE Metrics Calculator ─────────────────────
def calculate_ie_metrics(pdf, product_name, current_stock, price_per_unit):
    """
    Calculates all key IE inventory metrics for one product
    """
    prod = pdf[pdf["product_name"] == product_name]["qty_sold"]
    
    if len(prod) < 2:
        return None
    
    # --- Demand stats ---
    avg_daily_demand = prod.mean()
    std_daily_demand = prod.std()
    
    # --- Safety Stock ---
    # SS = Z × σ_demand × √(Lead Time)
    safety_stock = Z_SCORE * std_daily_demand * np.sqrt(LEAD_TIME_AVG)
    
    # --- Reorder Point ---
    # ROP = (Avg Daily Demand × Lead Time) + Safety Stock
    rop = (avg_daily_demand * LEAD_TIME_AVG) + safety_stock
    
    # --- EOQ (Economic Order Quantity) ---
    # EOQ = √(2 × Annual Demand × Ordering Cost / Holding Cost per unit)
    annual_demand = avg_daily_demand * WORKING_DAYS
    holding_cost  = price_per_unit * HOLDING_RATE
    if holding_cost > 0:
        eoq = np.sqrt((2 * annual_demand * ORDERING_COST) / holding_cost)
    else:
        eoq = avg_daily_demand * 7  # fallback: 1 week supply
    
    # --- Days of Supply ---
    dos = current_stock / avg_daily_demand if avg_daily_demand > 0 else 999
    
    # --- Urgency ---
    if dos <= LEAD_TIME_MIN:
        urgency = "🔴 CRITICAL"
    elif dos <= LEAD_TIME_MAX:
        urgency = "🟡 WARNING"
    elif current_stock <= rop:
        urgency = "🟠 REORDER"
    else:
        urgency = "🟢 OK"
    
    return {
        "product_name":      product_name,
        "avg_daily_demand":  round(avg_daily_demand, 2),
        "std_daily_demand":  round(std_daily_demand, 2),
        "safety_stock":      round(safety_stock, 2),
        "reorder_point":     round(rop, 2),
        "eoq":               round(eoq, 2),
        "days_of_supply":    round(dos, 1),
        "current_stock":     current_stock,
        "urgency":           urgency,
        "needs_reorder":     current_stock <= rop
    }

# Test
metrics = calculate_ie_metrics(pdf, "Tata Salt 1kg", 
                                current_stock=8, 
                                price_per_unit=22)
if metrics:
    for k, v in metrics.items():
        print(f"  {k}: {v}")
else:
    print("⚠️ Not enough data to calculate metrics")

# COMMAND ----------

# ─── CELL 5: Full pipeline — all products ──────────────
from datetime import datetime, date
from pyspark.sql import Row
import json, numpy as np

def run_full_ie_pipeline(shop_id, inventory_dict):
    """
    inventory_dict: {product_name: {current_stock, price_per_unit, unit}}
    Runs complete IE pipeline and writes to Delta tables
    """
    pdf   = load_sales_history(shop_id, days=30)
    today = date.today()
    results   = []
    alerts    = []
    forecasts = []

    # ── Load RAG prior from Delta ─────────────────────────
    prior_rows = spark.sql(f"""
        SELECT * FROM workspace.default.shop_priors
        WHERE shop_id = '{shop_id}'
        ORDER BY created_at DESC LIMIT 1
    """).collect()

    if prior_rows:
        pr = prior_rows[0]
        shop_prior = {
            "avg_amt_prior":     pr["avg_amt_prior"],
            "avg_amt_prior_inr": pr["avg_amt_prior_inr"],
            "seasonality_pattern": json.loads(pr["seasonality_pattern"])
        }
        prior_source = "rag"
    else:
        # Fallback if RAG notebook hasn't run yet
        shop_prior = {
            "avg_amt_prior":     100.0,
            "avg_amt_prior_inr": 8300.0,
            "seasonality_pattern": [1.0] * 52
        }
        prior_source = "fallback"
    print(f"   Prior source: {prior_source}")

    # ── Load local daily revenue history for Bayesian ─────
    local_history_rows = spark.sql(f"""
        SELECT date, SUM(total_amount) as daily_revenue
        FROM workspace.default.sales_log
        WHERE shop_id = '{shop_id}'
        GROUP BY date
        ORDER BY date
    """).toPandas()
    local_sales_history = local_history_rows["daily_revenue"].tolist()

    # ── Bayesian blend — shop level daily revenue ─────────
    n              = len(local_sales_history)
    prior_mean     = shop_prior["avg_amt_prior_inr"]
    prior_strength = 7  # prior counts as 7 virtual days

    if n == 0:
        posterior_daily_revenue = prior_mean
        prior_weight = 1.0
        data_weight  = 0.0
    else:
        real_mean    = float(np.mean(local_sales_history))
        prior_weight = prior_strength / (prior_strength + n)
        data_weight  = n / (prior_strength + n)
        posterior_daily_revenue = (prior_weight * prior_mean) + (data_weight * real_mean)

    # ── Festival/seasonality multiplier ───────────────────
    current_week = int(spark.sql(
        "SELECT WEEKOFYEAR(CURRENT_DATE()) AS w"
    ).collect()[0]["w"])
    seasonality  = shop_prior["seasonality_pattern"]
    avg_season   = float(np.mean(seasonality)) if seasonality else 1.0
    fest_mult    = (seasonality[current_week - 1] / avg_season
                    if avg_season > 0 else 1.0)
    adjusted_daily_revenue = posterior_daily_revenue * fest_mult

    print(f"   Days of real data : {n}")
    print(f"   Prior weight      : {prior_weight*100:.0f}%  |  Real data weight: {data_weight*100:.0f}%")
    print(f"   Posterior revenue : ₹{posterior_daily_revenue:,.0f}/day")
    print(f"   Festival mult     : {fest_mult:.3f}x  →  ₹{adjusted_daily_revenue:,.0f}/day adjusted")

    # ── Per-product loop ───────────────────────────────────
    for product_name, inv in inventory_dict.items():
        current_stock  = inv["current_stock"]
        price_per_unit = inv["price_per_unit"]
        unit           = inv.get("unit", "units")
        category       = inv.get("category", "General")

        # IE Metrics
        m = calculate_ie_metrics(pdf, product_name,
                                  current_stock, price_per_unit)
        if m is None:
            print(f"   ⚠️  Skipping {product_name} — not enough history")
            continue

        # EWM forecasts
        qty_1d,  amt_1d  = ewm_forecast(pdf, product_name, 1)
        qty_7d,  amt_7d  = ewm_forecast(pdf, product_name, 7)
        qty_30d, amt_30d = ewm_forecast(pdf, product_name, 30)

        # Scale EWM amount forecasts by Bayesian adjustment ratio
        # so product-level forecasts inherit the shop-level personalisation
        bayesian_ratio = (adjusted_daily_revenue / posterior_daily_revenue
                          if posterior_daily_revenue > 0 else 1.0)
        amt_1d_adj  = round(amt_1d  * bayesian_ratio, 2)
        amt_7d_adj  = round(amt_7d  * bayesian_ratio, 2)
        amt_30d_adj = round(amt_30d * bayesian_ratio, 2)

        # Reorder quantity = max(EOQ, 7-day demand)
        reorder_qty = max(m["eoq"], qty_7d)

        results.append({**m, "category": category, "unit": unit,
                         "bayesian_ratio": round(bayesian_ratio, 3)})

        # Log forecast — store both raw EWM and Bayesian-adjusted amounts
        forecasts.append(Row(
            shop_id          = shop_id,
            forecast_date    = today,
            product_name     = product_name,
            category         = category,
            forecast_1d_qty  = qty_1d,
            forecast_7d_qty  = qty_7d,
            forecast_30d_qty = qty_30d,
            forecast_1d_amt  = amt_1d_adj,   # Bayesian adjusted
            forecast_7d_amt  = amt_7d_adj,
            forecast_30d_amt = amt_30d_adj,
            method           = f"EWM_span7+Bayesian_{n}days_w{prior_weight:.2f}",
            created_at       = datetime.now()
        ))

        # Reorder alert if stock at or below ROP
        if m["needs_reorder"]:
            alerts.append(Row(
                shop_id        = shop_id,
                alert_date     = today,
                product_name   = product_name,
                category       = category,
                current_stock  = float(current_stock),
                days_remaining = float(m["days_of_supply"]),
                reorder_qty    = float(round(reorder_qty, 0)),
                rop            = float(m["reorder_point"]),
                urgency        = m["urgency"],
                resolved       = False,
                created_at     = datetime.now()
            ))

    # ── Write to Delta ─────────────────────────────────────
    if forecasts:
        spark.createDataFrame(forecasts).write \
            .format("delta").mode("append") \
            .saveAsTable("workspace.default.forecasts_log")

    if alerts:
        spark.createDataFrame(alerts).write \
            .format("delta").mode("append") \
            .saveAsTable("workspace.default.reorder_alerts")

    print(f"\n✅ Pipeline complete")
    print(f"   Products analyzed : {len(results)}")
    print(f"   Alerts generated  : {len(alerts)}")
    print(f"   Forecasts logged  : {len(forecasts)}")

    return pd.DataFrame(results), alerts, forecasts

# COMMAND ----------

# ─── CELL 6: Daily metrics summary ─────────────────────
def calculate_daily_metrics(shop_id):
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    row = spark.sql(f"""
        SELECT
            '{shop_id}'                        as shop_id,
            date,
            ROUND(SUM(total_amount), 2)        as total_revenue,
            CAST(SUM(qty_sold) AS INT)         as total_units,
            COUNT(DISTINCT product_name)       as products_moved,
            ROUND(AVG(total_amount), 2)        as avg_basket_value,
            FIRST(category)                    as top_category
        FROM workspace.default.sales_log
        WHERE shop_id = '{shop_id}'
          AND date = '{yesterday}'
        GROUP BY date
    """).collect()
    
    if not row:
        print("No sales data for yesterday")
        return None
    
    r = row[0]
    
    spark.createDataFrame([Row(
        shop_id             = shop_id,
        date                = yesterday,
        total_revenue       = float(r["total_revenue"] or 0),
        total_units         = int(r["total_units"] or 0),
        products_moved      = int(r["products_moved"] or 0),
        avg_basket_value    = float(r["avg_basket_value"] or 0),
        top_category        = str(r["top_category"] or ""),
        dos_avg             = 0.0,  # updated by IE pipeline
        stockout_risk_count = len(spark.sql(f"""
            SELECT * FROM workspace.default.reorder_alerts
            WHERE shop_id='{shop_id}' 
              AND alert_date='{today}'
              AND urgency='🔴 CRITICAL'
        """).collect()),
        calculated_at       = datetime.now()
    )]).write.format("delta").mode("append") \
      .saveAsTable("workspace.default.daily_metrics")
    
    print(f"✅ Daily metrics saved for {yesterday}")
    return r

# COMMAND ----------

# ─── CELL 7: Weekly stocking plan ──────────────────────
def generate_weekly_plan(shop_id, inventory_dict):
    """
    Every Monday — generates what to order this week
    Based on 7-day EWM forecast + EOQ
    """
    from datetime import date, timedelta
    pdf    = load_sales_history(shop_id, days=30)
    today  = date.today()
    week_start = today - timedelta(days=today.weekday())  # Monday
    
    plan_rows = []
    for product_name, inv in inventory_dict.items():
        qty_7d, amt_7d = ewm_forecast(pdf, product_name, 7)
        m = calculate_ie_metrics(pdf, product_name,
                                  inv["current_stock"],
                                  inv["price_per_unit"])
        if m is None:
            continue
        
        # Only include if stock will fall below ROP this week
        projected_stock = inv["current_stock"] - qty_7d
        if projected_stock <= m["reorder_point"]:
            recommend_qty = max(m["eoq"], qty_7d - inv["current_stock"])
            priority = "HIGH" if m["urgency"] in ["🔴 CRITICAL","🟡 WARNING"] \
                       else "MEDIUM"
            
            plan_rows.append(Row(
                shop_id         = shop_id,
                week_start      = week_start,
                product_name    = product_name,
                category        = inv.get("category","General"),
                recommended_qty = round(recommend_qty, 0),
                estimated_cost  = round(recommend_qty * inv["price_per_unit"], 2),
                priority        = priority,
                created_at      = datetime.now()
            ))
    
    if plan_rows:
        spark.createDataFrame(plan_rows).write \
            .format("delta").mode("append") \
            .saveAsTable("workspace.default.weekly_stocking_plan")
    
    print(f"✅ Weekly plan: {len(plan_rows)} products to restock")
    print(f"   Estimated total cost: ₹{sum(r.estimated_cost for r in plan_rows):,.0f}")
    return plan_rows

# COMMAND ----------

# ─── CELL 8: TEST RUN — paste your actual inventory ────
# Update current_stock with real values once CSV is loaded

inventory_dict = {
    "Shakti Bhog Atta 5kg":    {"current_stock": 10, "price_per_unit": 270, "unit": "bags",    "category": "Atta/Grains"},
    "Fortune Oil 1L":           {"current_stock": 8,  "price_per_unit": 145, "unit": "bottles", "category": "Oil/Ghee"},
    "Refined Sugar 1kg":        {"current_stock": 15, "price_per_unit": 44,  "unit": "packets", "category": "Salt/Sugar"},
    "Lays Chips 52g":           {"current_stock": 20, "price_per_unit": 20,  "unit": "packets", "category": "Biscuits/Snacks"},
    "Coca-Cola 250ml":          {"current_stock": 24, "price_per_unit": 20,  "unit": "bottles", "category": "Cold Drinks"},
    "Black Pepper 50g":         {"current_stock": 6,  "price_per_unit": 74,  "unit": "packets", "category": "Spices"},
    "Amul Butter 100g":         {"current_stock": 5,  "price_per_unit": 58,  "unit": "packets", "category": "Dairy"},
    "Wheat Flour Loose 1kg":    {"current_stock": 30, "price_per_unit": 34,  "unit": "kg",      "category": "Atta/Grains"},
    "Surf Excel 1kg":           {"current_stock": 4,  "price_per_unit": 215, "unit": "packets", "category": "Soap/Detergent"},
    "Sprite 250ml":             {"current_stock": 18, "price_per_unit": 20,  "unit": "bottles", "category": "Cold Drinks"},
}

results_df, alerts, forecasts = run_full_ie_pipeline(SHOP_ID, inventory_dict)

if not results_df.empty:
    print("\n📊 IE METRICS SUMMARY:")
    print(results_df[["product_name","avg_daily_demand","safety_stock",
                       "reorder_point","eoq","days_of_supply","urgency"]] \
          .sort_values("days_of_supply").to_string(index=False))
else:
    print("\n⚠️ No metrics generated — not enough sales data for any product")