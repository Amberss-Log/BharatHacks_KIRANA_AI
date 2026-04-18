# Databricks notebook source
print("Hello Group")

# COMMAND ----------

# MAGIC %md
# MAGIC # PERSON V

# COMMAND ----------

# df = spark.table("crisp_inc_cpg_retail_and_distributor_data_samples.examples.harmonized_retailer_sales")


# COMMAND ----------

# df

# COMMAND ----------

# df.columns

# COMMAND ----------

# DBTITLE 1,Cell 5
# df = spark.table("crisp_inc_cpg_retail_and_distributor_data_samples.examples.harmonized_retailer_sales")
# display(df.limit(5))

# COMMAND ----------

# DBTITLE 1,Cell 7
from pyspark.sql import functions as F

# Re-run this cell if you see NO_ACTIVE_SESSION error (after Cell 32's Python restart)
df = spark.table("crisp_inc_cpg_retail_and_distributor_data_samples.examples.harmonized_retailer_sales")
df_sample = df.sampleBy("store_state",fractions = {state: 0.1 for state in [row[0] for row in df.select("store_state").distinct().collect()]},
                        seed = 42)

# COMMAND ----------

# display(df_sample)

# COMMAND ----------

print(df_sample.count())

# COMMAND ----------

# MAGIC %md
# MAGIC ### Cleaning  

# COMMAND ----------

df_clean = df_sample.filter((F.col("sales_amount")>0) & (F.col("sales_quantity")>0) & (F.col("date_key") != "2022-09-10"))

df_clean = df_clean.withColumn("implied_price", F.col("sales_amount")/F.col("sales_quantity"))
# display(df_clean)
# df_clean.write.mode("overwrite").saveAsTable("sales_clean")

# COMMAND ----------

df_agg = df_clean.groupBy("date_key", "store_id", "product_id", "store_type", "store_state", "supplier").agg(F.sum("sales_quantity").alias("sales_quantity"), F.sum("sales_amount").alias("sales_amount"))

# df_agg.cache()
df_agg.count()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Features

# COMMAND ----------

df_features = df_agg.withColumn("date", F.to_date("date_key"))\
                    .withColumn("day_of_week", F.dayofweek("date"))\
                    .withColumn("week_of_year", F.weekofyear("date"))\
                    .withColumn("month", F.month("date"))\
                    .withColumn("is_weekend", (F.dayofweek("date").isin([1,7])).cast("int"))

# COMMAND ----------

# Adding lag features

from pyspark.sql.window import Window
w = Window.partitionBy("store_id", "product_id").orderBy("date_key")
df_features = (df_features \
                .withColumn("qty_lag_7", F.lag("sales_quantity", 7).over(w)) \
                .withColumn("qty_lag_14", F.lag("sales_quantity", 14).over(w)) \
                .withColumn("qty_lag_28", F.lag("sales_quantity", 28).over(w)) \
                .withColumn("amt_lag_7", F.lag("sales_amount", 7).over(w)) \
                .withColumn("amt_lag_14", F.lag("sales_amount", 14).over(w)) \
                .withColumn("amt_lag_28", F.lag("sales_amount", 28).over(w)))
# display(df_features)


# COMMAND ----------

# %pip install lightgbm

# COMMAND ----------

# dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Converting to pandas to train lgb

# COMMAND ----------

from pyspark.sql.functions import concat_ws

df_features = df_features.withColumn(
    "store_product_id", 
    concat_ws("_", F.col("store_id"), F.col("product_id"))
)

df_features = df_features \
    .withColumn("qty_roll_7", 
        F.avg("sales_quantity").over(w.rowsBetween(-7, -1))) \
    .withColumn("qty_roll_28", 
        F.avg("sales_quantity").over(w.rowsBetween(-28, -1))) \
    .withColumn("amt_roll_7", 
        F.avg("sales_amount").over(w.rowsBetween(-7, -1))) \
    .withColumn("amt_roll_28", 
        F.avg("sales_amount").over(w.rowsBetween(-28, -1)))
    
df_features = df_features.dropna()

# COMMAND ----------


pdf = df_features.toPandas()

from sklearn.preprocessing import LabelEncoder
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# COMMAND ----------

# DBTITLE 1,Cell 19
for col in ["store_id", "product_id", "store_type", "store_state", "supplier"]:
  pdf[col] = LabelEncoder().fit_transform(pdf[col].astype(str))
pdf["store_product_id"] = LabelEncoder().fit_transform(
    pdf["store_product_id"].astype(str)
)


# COMMAND ----------

# Convert numeric columns from object to numeric
for col in ["sales_quantity", "qty_lag_7", "qty_lag_14", "qty_lag_28", "amt_lag_7", "amt_lag_14", "amt_lag_28", "qty_roll_7", "qty_roll_28","amt_roll_7", "amt_roll_28"]:
  pdf[col] = pd.to_numeric(pdf[col], errors='coerce')

FEATURES = [
    "day_of_week",
    "week_of_year",
    "month",
    "is_weekend",
    "store_id",
    "product_id",
    "store_type",
    "store_state",
    "supplier",
    "qty_lag_7",
    "qty_lag_14",
    "qty_lag_28",
    "amt_lag_7",
    "amt_lag_14",
    "amt_lag_28",
    "qty_roll_7",
    "qty_roll_28",
    "amt_roll_7",
    "amt_roll_28"
]

# COMMAND ----------

FEATURES.append("store_product_id")

# COMMAND ----------

# Train aur test split - last 3 days of data for testing

cutoff = pdf["date"].max() - pd.Timedelta(days=30)
train_pdf = pdf[pdf["date"] <= cutoff]
test_pdf = pdf[pdf["date"] > cutoff]
# Train model

X_train, y_train_qty = train_pdf[FEATURES], train_pdf["sales_quantity"]
X_test, y_test_qty = test_pdf[FEATURES], test_pdf["sales_quantity"]

X_train, y_train_amt = train_pdf[FEATURES], train_pdf["sales_amount"]
X_test, y_test_amt = test_pdf[FEATURES], test_pdf["sales_amount"]

# COMMAND ----------

# DBTITLE 1,Cell 25
import mlflow
import mlflow.lightgbm
from mlflow.models.signature import infer_signature

# Set experiment name
mlflow.set_experiment("/Users/me230003086@iiti.ac.in/BharatBricks/sales_forecasting")

# Start MLflow run
with mlflow.start_run(run_name="lgb_dual_model_v1") as run:
    
    # Log parameters
    params = {
        "n_estimators": 300,
        "learning_rate": 0.05,
        "n_jobs": -1,
        "train_cutoff_days": 30,
        "features_count": len(FEATURES)
    }
    mlflow.log_params(params)
    
    # Train quantity model
    model_qty = lgb.LGBMRegressor(n_estimators=300, learning_rate=0.05, n_jobs=-1)
    model_qty.fit(X_train, y_train_qty)
    
    # Train amount model
    model_amt = lgb.LGBMRegressor(n_estimators=300, learning_rate=0.05, n_jobs=-1)
    model_amt.fit(X_train, y_train_amt)
    
    # Calculate and log metrics
    qty_r2 = model_qty.score(X_test, y_test_qty)
    amt_r2 = model_amt.score(X_test, y_test_amt)
    
    y_pred_qty = model_qty.predict(X_test)
    y_pred_amt = model_amt.predict(X_test)
    
    qty_rmse = np.sqrt(mean_squared_error(y_test_qty, y_pred_qty))
    amt_rmse = np.sqrt(mean_squared_error(y_test_amt, y_pred_amt))
    
    mlflow.log_metrics({
        "qty_r2": qty_r2,
        "amt_r2": amt_r2,
        "qty_rmse": qty_rmse,
        "amt_rmse": amt_rmse
    })
    
    print(f"Qty R^2: {qty_r2:.4f}, RMSE: {qty_rmse:.4f}")
    print(f"Amt R^2: {amt_r2:.4f}, RMSE: {amt_rmse:.4f}")
    
    # Log models with signatures
    signature_qty = infer_signature(X_train, y_train_qty)
    signature_amt = infer_signature(X_train, y_train_amt)
    
    mlflow.lightgbm.log_model(
        model_qty, 
        "quantity_model",
        signature=signature_qty,
        input_example=X_train.iloc[:5]
    )
    
    mlflow.lightgbm.log_model(
        model_amt, 
        "amount_model",
        signature=signature_amt,
        input_example=X_train.iloc[:5]
    )
    
    # Log feature importance plot
    fig, ax = plt.subplots(figsize=(10, 6))
    lgb.plot_importance(model_qty, ax=ax)
    plt.title("Feature Importance - Quantity Model")
    mlflow.log_figure(fig, "feature_importance_qty.png")
    plt.show()
    
    # Log feature list as artifact
    with open("/tmp/features.txt", "w") as f:
        f.write("\n".join(FEATURES))
    mlflow.log_artifact("/tmp/features.txt")
    
    print(f"\nMLflow Run ID: {run.info.run_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC Dumping in a pickle file

# COMMAND ----------

# DBTITLE 1,Model Registration
# Register models to Unity Catalog for production use
# This makes models accessible to your team

# Set your catalog and schema (update these to your workspace)
catalog = "workspace"  # or your catalog name
schema = "default"  # or your schema name

# Register quantity model
qty_model_name = f"{catalog}.{schema}.sales_quantity_forecast"
qty_model_version = mlflow.register_model(
    f"runs:/{run.info.run_id}/quantity_model",
    qty_model_name
)

print(f"Registered {qty_model_name} version {qty_model_version.version}")

# Register amount model
amt_model_name = f"{catalog}.{schema}.sales_amount_forecast"
amt_model_version = mlflow.register_model(
    f"runs:/{run.info.run_id}/amount_model",
    amt_model_name
)

print(f"Registered {amt_model_name} version {amt_model_version.version}")

# Add model descriptions (optional but recommended)
from mlflow.tracking import MlflowClient
client = MlflowClient()

client.update_registered_model(
    name=qty_model_name,
    description="LightGBM model for forecasting sales quantity. Uses lagged features, rolling averages, and temporal features. Trained on US retail data with Bayesian updating for new markets."
)

client.update_registered_model(
    name=amt_model_name,
    description="LightGBM model for forecasting sales amount (revenue). Uses lagged features, rolling averages, and temporal features. Trained on US retail data with Bayesian updating for new markets."
)

# COMMAND ----------

client = mlflow.tracking.MlflowClient()
model = client.get_registered_model(
    "workspace.default.sales_quantity_forecast"
)
print(f"Model found: {model.name}")
print(f"Latest version: {model.latest_versions[0].version}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Bayesian Updating Function

# COMMAND ----------

# DBTITLE 1,Load & Use Models
# Example: Load models from Unity Catalog and make predictions
# Anyone on your team with access can run this

# Load version 1 of models (change version number as needed)
qty_model_uri = f"models:/{catalog}.{schema}.sales_quantity_forecast/1"
amt_model_uri = f"models:/{catalog}.{schema}.sales_amount_forecast/1"

loaded_qty_model = mlflow.lightgbm.load_model(qty_model_uri)
loaded_amt_model = mlflow.lightgbm.load_model(amt_model_uri)

print("Models loaded successfully!")

# Make predictions on new data
# sample_features = X_test.iloc[0:1]  # Example: first test row
# qty_prediction = loaded_qty_model.predict(sample_features)
# amt_prediction = loaded_amt_model.predict(sample_features)
# print(f"Predicted Quantity: {qty_prediction[0]:.2f}")
# print(f"Predicted Amount: ${amt_prediction[0]:.2f}")

# Load specific version (e.g., version 2)
# qty_model_v2 = mlflow.lightgbm.load_model(f"models:/{catalog}.{schema}.sales_quantity_forecast/2")

# COMMAND ----------

def bayesian_forecast(model_qty, model_amt, shop_features, 
                       local_qty_history=None, local_amt_history=None):
    
    prior_qty = model_qty.predict([shop_features])[0]
    prior_amt = model_amt.predict([shop_features])[0]
    
    if local_qty_history is None or len(local_qty_history) == 0:
        return prior_qty, prior_amt  # cold start — pure US prior
    
    n_days = len(local_qty_history)
    # Weight shifts toward local data over 30 days
    w_local = min(n_days / 30, 0.8)
    
    local_qty = sum(local_qty_history) / n_days
    local_amt = sum(local_amt_history) / n_days
    
    posterior_qty = (1 - w_local) * prior_qty + w_local * local_qty
    posterior_amt = (1 - w_local) * prior_amt + w_local * local_amt
    
    return posterior_qty, posterior_amt

# COMMAND ----------

# MAGIC %md
# MAGIC # PERSON Ai

# COMMAND ----------

# MAGIC %md
# MAGIC ## Build or import your RAG here

# COMMAND ----------

