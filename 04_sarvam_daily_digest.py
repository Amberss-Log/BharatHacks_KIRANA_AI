# Databricks notebook source
# ─── CELL 1: Load everything from Delta ────────────────
import requests
import re
from pyspark.sql import Row
from datetime import date, timedelta, datetime

SHOP_ID        = "SHARMA_SIMROL_001"
# SARVAM_API_KEY 
SARVAM_API_KEY = dbutils.secrets.get(scope="aai", key="sarvam")

def get_digest_data(shop_id):
    # yesterday = date.today() - timedelta(days=1)
    # for demo mode:
    yesterday = "2025-03-30"  # last date in your CSV
    
    # Yesterday's sales summary
    sales = spark.sql(f"""
        SELECT 
            ROUND(SUM(total_amount),2)   as total_revenue,
            CAST(SUM(qty_sold) AS INT)   as total_units,
            COUNT(DISTINCT product_name) as products_moved
        FROM workspace.default.sales_log
        WHERE shop_id='{shop_id}' AND date='{yesterday}'
    """).collect()[0]
    
    # Top 3 products
    top3 = spark.sql(f"""
        SELECT product_name, category,
               SUM(qty_sold) as qty, 
               SUM(total_amount) as revenue
        FROM workspace.default.sales_log
        WHERE shop_id='{shop_id}' AND date='{yesterday}'
        GROUP BY product_name, category
        ORDER BY revenue DESC LIMIT 3
    """).collect()
    
    # Active alerts (handle if table doesn't exist)
    try:
        alerts = spark.sql(f"""
            SELECT product_name, current_stock, 
                   days_remaining, reorder_qty, urgency
            FROM workspace.default.reorder_alerts
            WHERE shop_id='{shop_id}' 
              AND alert_date='{date.today()}'
              AND resolved=false
            ORDER BY days_remaining ASC
        """).collect()
    except:
        alerts = []
    
    # 7 day forecast totals (handle if table doesn't exist)
    try:
        forecast = spark.sql(f"""
            SELECT product_name,
                   forecast_1d_qty, forecast_7d_qty, forecast_30d_qty,
                   forecast_1d_amt, forecast_7d_amt, forecast_30d_amt
            FROM workspace.default.forecasts_log
            WHERE shop_id='{shop_id}'
              AND forecast_date='{date.today()}'
            ORDER BY forecast_7d_amt DESC
            LIMIT 5
        """).collect()
    except:
        forecast = []
    
    return {
        "yesterday": str(yesterday),
        "sales": sales,
        "top3": top3,
        "alerts": alerts,
        "forecast": forecast
    }

# COMMAND ----------

# ─── CELL 2: Build prompt from Delta data ──────────────
def build_digest_prompt(data):
    s = data["sales"]
    
    top_text = "\n".join([
        f"- {r['product_name']} ({r['category']}): "
        f"{r['qty']:.0f} units, ₹{r['revenue']:.0f}"
        for r in data["top3"]
    ])
    
    alert_text = "\n".join([
        f"- {r['urgency']} {r['product_name']}: "
        f"{r['current_stock']:.0f} bachi, "
        f"{r['days_remaining']:.1f} din mein khatam, "
        f"order karo {r['reorder_qty']:.0f} units"
        for r in data["alerts"]
    ]) or "✅ Koi urgent alert nahi"
    
    forecast_text = "\n".join([
        f"- {r['product_name']}: "
        f"Kal {r['forecast_1d_qty']:.1f} | "
        f"7 din {r['forecast_7d_qty']:.1f} | "
        f"30 din {r['forecast_30d_qty']:.1f} units"
        for r in data["forecast"]
    ])
    
    return f"""
Dukaan: Sharma Ji Kirana Store, Simrol, Indore MP
Date: {data['yesterday']}

KAL KI BIKRI:
- Total Kamai: ₹{s['total_revenue'] or 0}
- Biki Units: {s['total_units'] or 0}
- Products Move Hue: {s['products_moved'] or 0}

TOP 3 PRODUCTS:
{top_text}

STOCK ALERTS (IE Calculated):
{alert_text}

FORECAST (EWM Model):
{forecast_text}

Inke basis pe daily digest banao with EXACTLY these sections:

🏆 KAL KA PERFORMANCE
(2 lines, numbers ke saath, motivating tone)

🚨 URGENT REORDER  
(Har critical item — exact quantity, reason, aur kitne din bacha)

📅 7 DIN KA STOCKING PLAN
(Top 5 products jo is hafte stock karne hain — quantity ke saath)

📈 30 DIN KA OUTLOOK
(Kya trend dikh raha hai — kaunsa category badhega, kaunsa season aa raha)

📦 AAJ KARNA HAI
(3 specific actions — numbered, actionable)

💡 SMART INSIGHT
(Ek cheez jo data mein dikh rahi hai jo owner shayad nahi dekh raha)

📱 WHATSAPP MESSAGE
(50 words, casual Hindi, jaise kisi dost ka message, 
emojis allowed, numbers must)

Har section data se linked hona chahiye. Vague mat bolna.
"""

# COMMAND ----------

# ─── CELL 3: Master daily runner ───────────────────────
def run_daily_digest():
    print("🚀 Sharma Ji Ka Daily Digest Chal Raha Hai...")
    
    data   = get_digest_data(SHOP_ID)
    prompt = build_digest_prompt(data)
    
    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sarvam-m",
        "messages": [
            {
                "role": "system",
                "content": """Tu ek smart retail advisor hai Indian kirana shops ke liye.
                Hamesha Hindi mein jawab de.
                Numbers specific rakho, data se linked rakho.
                Ek trusted local dost ki tarah baat karo, robot ki tarah nahi."""
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1200
    }
    
    resp = requests.post(
        "https://api.sarvam.ai/v1/chat/completions",
        headers=headers, json=payload
    )
    
    # digest = resp.json()["choices"][0]["message"]["content"]
    raw = resp.json()["choices"][0]["message"]["content"]
    digest = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()
    
    print("\n" + "="*60)
    print("📋 SHARMA JI KA AAJKA DIGEST")
    print("="*60)
    print(digest)
    print("="*60)
    
    # Save digest to Delta
    spark.createDataFrame([Row(
        shop_id   = SHOP_ID,
        date      = str(date.today()),
        digest    = digest,
        language  = "hi",
        created_at= datetime.now()
    )]).write.format("delta").mode("append") \
      .saveAsTable("workspace.default.daily_digests")
    
    return digest

digest = run_daily_digest()