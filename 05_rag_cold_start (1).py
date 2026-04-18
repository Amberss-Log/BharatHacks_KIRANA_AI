# Databricks notebook source
# MAGIC %pip install faiss-cpu

# COMMAND ----------

# MAGIC %restart_python

# COMMAND ----------

import numpy as np
import faiss
import pandas as pd

print("Loading store profiles from Delta table...")
profiles_pd = spark.table("workspace.default.store_profiles_agg").toPandas()
store_ids   = profiles_pd["store_id"].tolist()
print(f"Loaded {len(store_ids)} store profiles.")

# ── feature vector builder ───────────────────────────────────────────────────
def build_vector(avg_transaction, avg_qty, product_variety,
                 transaction_count, total_revenue):
    vec = np.array([
        float(avg_transaction)  / 100.0,
        float(avg_qty)          / 50.0,
        float(product_variety)  / 2000.0,
        np.log1p(float(transaction_count)) / 20.0,
        float(total_revenue)    / 1_000_000.0,
    ], dtype=np.float32)
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec

# ── build FAISS index ────────────────────────────────────────────────────────
print("Building FAISS index...")
vectors = np.stack([
    build_vector(
        r["avg_transaction"], r["avg_qty"],
        r["product_variety"], r["transaction_count"],
        r["total_revenue"]
    )
    for _, r in profiles_pd.iterrows()
])
faiss_index = faiss.IndexFlatL2(vectors.shape[1])
faiss.normalize_L2(vectors)
faiss_index.add(vectors)
print(f"FAISS index ready. {faiss_index.ntotal} vectors indexed.")

# COMMAND ----------

def find_similar_stores(shop: dict, top_k: int = 5) -> dict:
    """
    Takes a new Indian kirana's profile.
    Returns top 5 most similar US stores as Bayesian prior.
    """
    INR = 83.0
    
    query_vec = build_vector(
        avg_transaction   = shop.get("avg_transaction_inr", 200) / INR,
        avg_qty           = shop.get("avg_qty_per_bill", 5),
        product_variety   = shop.get("product_variety", 100),
        transaction_count = shop.get("daily_transactions", 50) * 365,
        total_revenue     = shop.get("monthly_revenue_inr", 100000) * 12 / INR
    ).reshape(1, -1)
    
    faiss.normalize_L2(query_vec)
    distances, indices = faiss_index.search(query_vec, top_k)
    
    confidence    = float(max(0.0, 1.0 - distances[0][0] / 2.0))
    matched_ids   = [store_ids[i]        for i in indices[0]]
    matched_profs = [profiles_pd.iloc[i] for i in indices[0]]
    
    avg_qty_prior = float(np.mean([p["avg_qty"]         for p in matched_profs]))
    avg_amt_prior = float(np.mean([p["avg_transaction"] for p in matched_profs]))
    
    result = {
        "matched_store_ids": matched_ids,
        "avg_qty_prior":     round(avg_qty_prior, 2),
        "avg_amt_prior":     round(avg_amt_prior, 2),
        "confidence_score":  round(confidence, 3),
        "flag":              None
    }
    
    # Fallback to national average if poor match
    if confidence < 0.5:
        result["avg_amt_prior"] = round(float(profiles_pd["avg_transaction"].mean()), 2)
        result["avg_qty_prior"] = round(float(profiles_pd["avg_qty"].mean()), 2)
        result["flag"]          = "low_confidence — using national average"
    
    return result


def get_seasonality(matched_store_ids: list) -> list:
    """
    Returns 52-week seasonality pattern.
    Uses shape from all 716M rows, scaled to matched store base level.
    """
    # Full year shape from all stores
    all_pattern = spark.sql("""
        SELECT 
            WEEKOFYEAR(date_key) AS week_num,
            AVG(sales_amount)    AS avg_rev
        FROM workspace.default.sales_data
        GROUP BY WEEKOFYEAR(date_key)
        ORDER BY week_num
    """).toPandas()
    
    # Base level from matched stores only
    ids_str    = ", ".join(str(i) for i in matched_store_ids)
    base_level = spark.sql(f"""
        SELECT AVG(sales_amount) AS base
        FROM workspace.default.sales_data
        WHERE store_id IN ({ids_str})
    """).toPandas()["base"][0]
    
    global_avg = float(all_pattern["avg_rev"].mean())
    index_map  = dict(zip(
        all_pattern["week_num"],
        all_pattern["avg_rev"] / global_avg
    ))
    
    pattern = [
        round(float(base_level * index_map.get(w, 1.0)), 2)
        for w in range(1, 53)
    ]
    
    return pattern


def get_cold_start_prior(shop_form: dict) -> dict:
    """
    Master function — call this at onboarding.
    Returns everything needed for the Bayesian model.
    """
    prior = find_similar_stores(shop_form)
    prior["seasonality_pattern"] = get_seasonality(prior["matched_store_ids"])
    prior["avg_amt_prior_inr"]   = round(prior["avg_amt_prior"] * 83.0, 2)
    prior["data_source"]         = "crisp_cpg_us_benchmark"
    return prior

print("RAG functions defined.")

# COMMAND ----------

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

# COMMAND ----------

# Sample kirana onboarding form
shop_form = {
    "avg_transaction_inr":  180,
    "avg_qty_per_bill":     6,
    "product_variety":      150,
    "daily_transactions":   80,
    "monthly_revenue_inr":  120000
}

# Step 1: get prior from RAG (runs once at onboarding)
print("Running RAG matching...")
prior = get_cold_start_prior(shop_form)

print("\n=== PRIOR FROM RAG ===")
for k, v in prior.items():
    if k == "seasonality_pattern":
        print(f"  seasonality_pattern: {v[:4]}... (52 weeks)")
    else:
        print(f"  {k}: {v}")

# Step 2: Day 0 forecast — no sales yet
result_day0 = bayesian_forecast(
    shop_id              = "SHOP_MP_001",
    prior                = prior,
    local_sales_history  = []
)

print("\n=== DAY 0 FORECAST (pure RAG prior) ===")
for k, v in result_day0.items():
    print(f"  {k}: {v}")

# COMMAND ----------

# Simulate a week of real sales coming in day by day
actual_sales = [9500, 11200, 8800, 10100, 12400, 9900, 10800]

print("=== BAYESIAN PRIOR DECAY OVER TIME ===")
print(f"{'Day':<6} {'Prior %':<10} {'Real %':<10} {'Forecast INR/day':<20} {'Source'}")
print("-" * 65)

for day in range(8):
    history = actual_sales[:day]  # grows each day
    r = bayesian_forecast("SHOP_MP_001", prior, history)
    print(
        f"  {day:<4} "
        f"  {r['prior_weight']*100:.0f}%{'':<6} "
        f"  {r['data_weight']*100:.0f}%{'':<6} "
        f"  ₹{r['adjusted_forecast_inr']:>10,.2f}       "
        f"  {r['source']}"
    )

# COMMAND ----------



# Quick test of full handoff
print("=== HANDOFF TEST ===")
shop = {
    "avg_transaction_inr":  180,
    "avg_qty_per_bill":     6,
    "product_variety":      150,
    "daily_transactions":   80,
    "monthly_revenue_inr":  120000
}

prior    = get_cold_start_prior(shop)
forecast = bayesian_forecast("SHOP_MP_001", prior, [9500, 11200, 8800])

print(f"  adjusted_forecast_inr : ₹{forecast['adjusted_forecast_inr']:,.2f}")
print(f"  prior_weight          : {forecast['prior_weight']*100:.0f}% (RAG)")
print(f"  data_weight           : {forecast['data_weight']*100:.0f}% (real sales)")
print(f"  festival_multiplier   : {forecast['festival_multiplier']}x")
print(f"  days_of_real_data     : {forecast['days_of_real_data']}")
print(f"  source                : {forecast['source']}")
print("\nRAG + Bayesian layer complete.")

# COMMAND ----------

