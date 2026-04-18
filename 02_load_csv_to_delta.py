# Databricks notebook source
# ─── CELL 1: Load CSV into Delta sales_log ─────────────
# Upload your CSV to Databricks first:
# Databricks → Catalog → workspace → default → csv_uploads volume
# Upload your CSV there. The path will be: /Volumes/workspace/default/csv_uploads/sharma_sales_30days.csv

import uuid
from pyspark.sql import functions as F

df_csv = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load("/Volumes/workspace/default/csv_uploads/kirana_high_density_sales.csv")

# Preview
df_csv.show(5)
print(f"Total rows: {df_csv.count()}")

# COMMAND ----------

# ─── CELL 2: Clean and add required columns ─────────────
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
import uuid

# UDF for unique log IDs
uuid_udf = udf(lambda: str(uuid.uuid4()), StringType())

df_clean = df_csv \
    .withColumn("log_id", uuid_udf()) \
    .withColumn("shop_id", F.lit("SHARMA_SIMROL_001")) \
    .withColumn("date", F.to_date("date", "yyyy-MM-dd")) \
    .withColumn("qty_sold", F.col("qty_sold").cast("double")) \
    .withColumn("price_per_unit", F.col("price_per_unit").cast("double")) \
    .withColumn("total_amount", F.col("total_amount").cast("double")) \
    .withColumn("logged_at", F.current_timestamp()) \
    .select(
        "log_id", "shop_id", "date", "product_name",
        "category", "qty_sold", "price_per_unit",
        "total_amount", "logged_at"
    )

df_clean.show(5)
print(f"Clean rows: {df_clean.count()}")

# COMMAND ----------

# ─── CELL 3: Write to Delta table ──────────────────────
df_clean.write \
    .format("delta") \
    .mode("append") \
    .saveAsTable("workspace.default.sales_log")

print("✅ Sales data loaded to Delta table")

# Verify
spark.sql("""
    SELECT date, COUNT(*) as entries, 
           SUM(total_amount) as daily_revenue
    FROM workspace.default.sales_log
    WHERE shop_id = 'SHARMA_SIMROL_001'
    GROUP BY date
    ORDER BY date
""").show(35)

# COMMAND ----------

# ─── CELL 4: Demo live append function ─────────────────
# This simulates a shopkeeper logging a new sale in real time

from pyspark.sql import Row
from pyspark.sql import functions as F
from datetime import datetime, date as dt
import uuid

def log_sale(product_name, category, qty_sold, price_per_unit, date=None):
    """
    Shopkeeper calls this whenever a sale happens.
    In demo: run this cell with new values.
    In production: connected to a simple mobile form.
    """
    sale_date = date if date else dt.today()
    
    row = Row(
        log_id        = str(uuid.uuid4()),
        shop_id       = "SHARMA_SIMROL_001",
        date          = sale_date,
        product_name  = product_name,
        category      = category,
        qty_sold      = float(qty_sold),
        price_per_unit= float(price_per_unit),
        total_amount  = float(qty_sold * price_per_unit),
        logged_at     = datetime.now()
    )
    
    spark.createDataFrame([row]).write \
        .format("delta") \
        .mode("append") \
        .saveAsTable("workspace.default.sales_log")
    
    print(f"✅ Logged: {qty_sold} x {product_name} = ₹{qty_sold*price_per_unit:.0f}")

# Test it
log_sale("Tata Salt 1kg", "Salt/Sugar", 3, 22)
log_sale("Fortune Oil 1L", "Oil/Ghee", 2, 145)