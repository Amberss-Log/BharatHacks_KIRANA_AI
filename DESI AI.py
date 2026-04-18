# Databricks notebook source
# MAGIC %pip install sarvamai openai requests lightgbm

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

import mlflow
import mlflow.lightgbm
import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# COMMAND ----------

# Run this after restart
import mlflow.lightgbm
import mlflow

catalog = "workspace"
schema = "default"

model_qty = mlflow.lightgbm.load_model(
    f"models:/{catalog}.{schema}.sales_quantity_forecast/2"
)

model_amt = mlflow.lightgbm.load_model(
    f"models:/{catalog}.{schema}.sales_amount_forecast/2"
)

print("✅ model_qty loaded")
print("✅ model_amt loaded")

# COMMAND ----------

# Enable auto-tracing for OpenAI
mlflow.openai.autolog()

# COMMAND ----------

SARVAM_API_KEY = dbutils.secrets.get(scope="aai", key="sarvam")

# COMMAND ----------

text = "Jai Hind, welcome to Vyapaar Mitra"

# COMMAND ----------

import requests

def call_sarvam(prompt, language="hi"):
    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sarvam-m",
        "messages": [
            {
                "role": "system",
                "content": f"""You are a smart retail business advisor for Indian kirana shop owners.
                Respond in {'Hindi' if language == 'hi' else 'English'}.
                Be practical, specific, and sound like a trusted local advisor."""
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    response = requests.post(
        "https://api.sarvam.ai/v1/chat/completions",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

# Quick test
test = call_sarvam("Meri shop mein kal 50kg chawal aur 20L tel bika. Kya mujhe aaj reorder karna chahiye?", language="hi")
print(test)

# COMMAND ----------

# DBTITLE 1,Cell 12
# ─── CELL 1: Imports ───────────────────────────────────
import requests, json, pandas as pd, numpy as np
from datetime import datetime, timedelta
from pyspark.sql import functions as F

# SARVAM_API_KEY = "your_key_here"  # move to secrets later

# ─── CELL 2: Sarvam caller ─────────────────────────────
def call_sarvam(prompt, language="hi"):
    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json"
    }
    lang_instruction = "Hindi" if language == "hi" else "English"
    
    payload = {
        "model": "sarvam-m",
        "messages": [
            {
                "role": "system",
                "content": f"""You are a smart retail business advisor for Indian kirana and grocery shop owners.
                Always respond in {lang_instruction}.
                Use simple language, be specific with numbers, sound like a trusted local advisor.
                Format output with clear emoji section headers.
                Never give vague advice — always tie it to the actual data given."""
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    response = requests.post(
        "https://api.sarvam.ai/v1/chat/completions",
        headers=headers, json=payload
    )
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

# COMMAND ----------

# ─── CELL 3: Bayesian forecast function ────────────────
def bayesian_forecast(prior_qty, prior_amt, 
                       local_qty_history=None, 
                       local_amt_history=None):
    if not local_qty_history:
        return round(prior_qty, 2), round(prior_amt, 2)
    
    n_days = len(local_qty_history)
    w_local = min(n_days / 30, 0.8)
    
    local_qty = sum(local_qty_history) / n_days
    local_amt = sum(local_amt_history) / n_days
    
    posterior_qty = (1 - w_local) * prior_qty + w_local * local_qty
    posterior_amt = (1 - w_local) * prior_amt + w_local * local_amt
    
    return round(posterior_qty, 2), round(posterior_amt, 2)

# COMMAND ----------

from pyspark.sql import functions as F
from datetime import datetime, timedelta

def get_yesterday_summary(shop_id):
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Access shared variables/data using dbutils.notebook.run or Delta tables
    # Example: dbutils.notebook.run("other_notebook", 60, {"shop_id": shop_id})
    # Or read shared Delta table directly as below

    df = spark.table("sales_log") \
        .filter(F.col("store_id") == shop_id) \
        .filter(F.col("date_key") == yesterday)
    
    summary = df.agg(
        F.sum("sales_amount").alias("total_revenue"),
        F.sum("sales_quantity").alias("total_units"),
        F.countDistinct("product_id").alias("products_sold")
    ).collect()[0]
    
    top_products = df.groupBy("product_id").agg(
        F.sum("sales_quantity").alias("qty"),
        F.sum("sales_amount").alias("revenue")
    ).orderBy(F.desc("revenue")).limit(3).collect()
    
    alerts = get_reorder_alerts(shop_id)
    
    return {
        "date": yesterday,
        "shop_id": shop_id,
        "total_revenue": round(float(summary["total_revenue"]), 2),
        "total_units": int(summary["total_units"]),
        "products_sold": int(summary["products_sold"]),
        "top_products": [row.asDict() for row in top_products],
        "reorder_alerts": alerts
    }

# COMMAND ----------

# ─── CELL 4: Reorder alert generator ───────────────────
def get_reorder_alerts(shop_inventory, model_qty, features_dict):
    """
    shop_inventory: list of dicts with product, current_stock, features
    Returns alerts sorted by urgency
    """
    alerts = []
    
    for item in shop_inventory:
        features_df = pd.DataFrame([item["features"]])[FEATURES]
        predicted_daily = model_qty.predict(features_df)[0]
        predicted_daily = max(predicted_daily, 0.1)
        
        days_remaining = item["current_stock"] / predicted_daily
        reorder_qty = int(predicted_daily * 7)  # 1 week buffer
        
        if days_remaining <= 5:  # alert threshold
            alerts.append({
                "product": item["product_name"],
                "current_stock": item["current_stock"],
                "unit": item.get("unit", "units"),
                "days_remaining": round(days_remaining, 1),
                "reorder_qty": reorder_qty,
                "urgency": "🔴 CRITICAL" if days_remaining <= 2 else "🟡 WARNING"
            })
    
    return sorted(alerts, key=lambda x: x["days_remaining"])

# COMMAND ----------

# ─── CELL 5: Prompt builder ────────────────────────────
def build_daily_prompt(shop_profile, sales_summary, alerts, forecasts):
    
    alerts_text = ""
    for a in alerts:
        alerts_text += (
            f"- {a['urgency']} {a['product']}: "
            f"{a['current_stock']} {a['unit']} bacha hai, "
            f"{a['days_remaining']} din mein khatam. "
            f"Reorder: {a['reorder_qty']} {a['unit']}\n"
        )
    
    top_text = ""
    for p in sales_summary["top_products"]:
        top_text += f"- {p['name']}: {p['qty']} units, ₹{p['revenue']:.0f}\n"
    
    forecast_text = ""
    for f in forecasts:
        forecast_text += (
            f"- {f['product']}: "
            f"Kal {f['predicted_qty']} units bikne ka estimate, "
            f"₹{f['predicted_amt']:.0f} revenue\n"
        )
    
    prompt = f"""
Dukaan: {shop_profile['name']}
Location: {shop_profile['location']} | Type: {shop_profile['type']}
Date: {sales_summary['date']}

KAL KI BIKRI (Yesterday's Sales):
- Total Revenue: ₹{sales_summary['total_revenue']}
- Total Units: {sales_summary['total_units']}
- Products Moved: {sales_summary['products_moved']}

TOP PRODUCTS:
{top_text}

STOCK ALERTS:
{alerts_text if alerts_text else "✅ Koi critical alert nahi hai aaj."}

AAJ KA FORECAST:
{forecast_text}

Ab ek daily business digest banao with EXACTLY these sections:

🏆 KAL KA PERFORMANCE
(2 lines — numbers ke saath, positive tone)

🚨 URGENT REORDER
(Sirf critical items — exact quantity batao, reason batao)

📦 AAJ KARNA HAI
(3 specific action items — actionable, numbered)

💡 SMART TIP
(Ek insight jo owner shayad miss kar raha hai — data se linked)

📱 WHATSAPP MESSAGE
(Ek short paragraph — casual Hindi, jaise dost ko bhej rahe ho,
under 50 words, emojis allowed)

Har section mein numbers use karo. Vague mat bolo.
"""
    return prompt

# COMMAND ----------

# ─── CELL 6: Query handler ─────────────────────────────
def handle_owner_query(query, shop_profile, sales_summary, language="hi"):
    """
    Owner sends any question — system answers with shop context
    """
    prompt = f"""
Shop context:
- Dukaan: {shop_profile['name']}, {shop_profile['location']}
- Kal ki kamai: ₹{sales_summary['total_revenue']}
- Total units: {sales_summary['total_units']}

Owner ka sawaal: "{query}"

Instructions:
- Sirf pooche gaye sawaal ka jawab do
- Data se linked specific answer do
- 100 words se kam rakho
- End mein ek actionable suggestion do
"""
    return call_sarvam(prompt, language)

# COMMAND ----------

# ─── CELL 7: Master daily runner ───────────────────────
def run_daily_digest(shop_profile, shop_inventory, local_history=None):
    
    print(f"🚀 Running daily digest for {shop_profile['name']}...")
    
    # --- Mock sales summary (replace with Delta table query) ---
    sales_summary = {
        "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "total_revenue": 18450.0,
        "total_units": 312,
        "products_moved": 28,
        "top_products": [
            {"name": "Tata Salt 1kg", "qty": 45, "revenue": 2025},
            {"name": "Aashirvaad Aata 5kg", "qty": 18, "revenue": 2160},
            {"name": "Fortune Oil 1L", "qty": 22, "revenue": 2860},
        ]
    }
    
    # --- Get reorder alerts ---
    alerts = get_reorder_alerts(shop_inventory, model_qty, FEATURES)
    
    # --- Get forecasts with Bayesian updating ---
    forecasts = []
    for item in shop_inventory[:3]:  # top 3 products
        features_df = pd.DataFrame([item["features"]])[FEATURES]
        prior_qty = model_qty.predict(features_df)[0]
        prior_amt = model_amt.predict(features_df)[0]
        
        post_qty, post_amt = bayesian_forecast(
            prior_qty, prior_amt,
            local_history.get(item["product_name"], {}).get("qty", []),
            local_history.get(item["product_name"], {}).get("amt", [])
        )
        forecasts.append({
            "product": item["product_name"],
            "predicted_qty": post_qty,
            "predicted_amt": post_amt
        })
    
    # --- Build prompt and call Sarvam ---
    prompt = build_daily_prompt(
        shop_profile, sales_summary, alerts, forecasts
    )
    digest = call_sarvam(prompt, shop_profile.get("language", "hi"))
    
    print("\n" + "="*50)
    print(digest)
    print("="*50)
    
    return digest

# COMMAND ----------

# MAGIC %md
# MAGIC ### TEST

# COMMAND ----------

FEATURES = [
    "day_of_week", "week_of_year", "month", "is_weekend",
    "store_id", "product_id", "store_type", "store_state", "supplier",
    "qty_lag_7", "qty_lag_14", "qty_lag_28",
    "amt_lag_7", "amt_lag_14", "amt_lag_28",
    "qty_roll_7", "qty_roll_28",
    "amt_roll_7", "amt_roll_28",
    "store_product_id"
]

# COMMAND ----------

"features": {
    "day_of_week": 4,           # Thursday
    "week_of_year": 16,         # current week
    "month": 4,                  # April
    "is_weekend": 0,
    "store_id": 123,             # encoded store ID
    "product_id": 456,           # encoded product ID
    "store_type": 2,             # encoded
    "store_state": 8,            # encoded
    "supplier": 3,               # encoded
    "qty_lag_7": 45.0,           # units sold 7 days ago
    "qty_lag_14": 38.0,
    "qty_lag_28": 42.0,
    "amt_lag_7": 2025.0,         # revenue 7 days ago
    "amt_lag_14": 1710.0,
    "amt_lag_28": 1890.0,
    "qty_roll_7": 41.2,          # 7 day rolling average qty
    "qty_roll_28": 40.5,
    "amt_roll_7": 1850.0,
    "amt_roll_28": 1780.0,
    "store_product_id": 789      # encoded store+product combo
}

# COMMAND ----------

# ─── CELL 8: TEST RUN ──────────────────────────────────
shop_profile = {
    "name": "Sharma General Store",
    "location": "Indore, MP",
    "type": "Kirana",
    "language": "hi"
}

# Mock inventory — replace with your actual stock table
shop_inventory = [
    {
        "product_name": "Tata Salt 1kg",
        "current_stock": 8,
        "unit": "packets",
        "features": {f: 0 for f in FEATURES}  # replace with real features
    },
    {
        "product_name": "Fortune Oil 1L", 
        "current_stock": 3,
        "unit": "bottles",
        "features": {f: 0 for f in FEATURES}
    }
]

# Local history — grows daily as shop uses the app
local_history = {
    "Tata Salt 1kg": {"qty": [40, 45, 38, 42], "amt": [1800, 2025, 1710, 1890]},
    "Fortune Oil 1L": {"qty": [20, 22, 18, 25], "amt": [2600, 2860, 2340, 3250]}
}

digest = run_daily_digest(shop_profile, shop_inventory, local_history)