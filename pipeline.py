from pathlib import Path
import sqlite3
import pandas as pd

def find_data_dir():
    return next(Path(r"C:\Users\ADMIN\Downloads").rglob("olist_orders_dataset.csv")).parent

def extract_bronze(data_dir):
    files = {
        "orders": "olist_orders_dataset.csv",
        "order_items": "olist_order_items_dataset.csv",
        "payments": "olist_order_payments_dataset.csv",
        "reviews": "olist_order_reviews_dataset.csv",
        "customers": "olist_customers_dataset.csv",
        "products": "olist_products_dataset.csv",
        "sellers": "olist_sellers_dataset.csv",
        "geolocation": "olist_geolocation_dataset.csv",
        "category_translation": "product_category_name_translation.csv",}
    return {name: pd.read_csv(data_dir / fname) for name, fname in files.items()}

def transform_silver(bronze):
    orders = bronze["orders"].copy()
    date_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",]
    for col in date_cols:
        orders[col] = pd.to_datetime(orders[col])

    orders["delivery_days"] = (orders["order_delivered_customer_date"] - orders["order_purchase_timestamp"]).dt.total_seconds() / 86400
    orders["is_late"] = (orders["order_delivered_customer_date"] > orders["order_estimated_delivery_date"])
    orders = orders[orders["delivery_days"].isna() | (orders["delivery_days"] >= 0)].copy()

    products = bronze["products"].merge(bronze["category_translation"], on="product_category_name", how="left")
    products["product_category_name"] = products["product_category_name"].fillna("unknown")
    products["product_category_name_english"] = products["product_category_name_english"].fillna(products["product_category_name"])

    num_cols = [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",]
    for col in num_cols:
        products[col] = products[col].fillna(products[col].median())

    geo = bronze["geolocation"].copy()
    geo = geo[
        geo["geolocation_lat"].between(-34, 6)
        & geo["geolocation_lng"].between(-75, -32)].copy()
    geo["geolocation_city"] = geo["geolocation_city"].astype(str).str.strip().str.lower()
    geo["geolocation_state"] = geo["geolocation_state"].astype(str).str.strip().str.upper()
    geolocation = geo.groupby("geolocation_zip_code_prefix", as_index=False).agg(
        lat=("geolocation_lat", "mean"),
        lng=("geolocation_lng", "mean"),
        city=("geolocation_city", "first"),
        state=("geolocation_state", "first"),)

    customers = bronze["customers"].drop_duplicates(subset=["customer_id"]).copy()
    customers["customer_city"] = customers["customer_city"].astype(str).str.strip().str.lower()
    customers["customer_state"] = customers["customer_state"].astype(str).str.strip().str.upper()

    sellers = bronze["sellers"].drop_duplicates(subset=["seller_id"]).copy()
    sellers["seller_city"] = sellers["seller_city"].astype(str).str.strip().str.lower()
    sellers["seller_state"] = sellers["seller_state"].astype(str).str.strip().str.upper()

    reviews = bronze["reviews"].drop_duplicates(subset=["review_id"]).copy()
    reviews["review_creation_date"] = pd.to_datetime(reviews["review_creation_date"])
    reviews["review_answer_timestamp"] = pd.to_datetime(reviews["review_answer_timestamp"])

    order_items = bronze["order_items"].drop_duplicates().copy()
    order_items["shipping_limit_date"] = pd.to_datetime(order_items["shipping_limit_date"])
    order_items["total_item_value"] = order_items["price"] + order_items["freight_value"]

    silver = {
        "fact_orders": orders,
        "fact_order_items": order_items,
        "fact_payments": bronze["payments"].drop_duplicates().copy(),
        "fact_reviews": reviews,
        "dim_customers": customers,
        "dim_products": products.drop_duplicates(subset=["product_id"]),
        "dim_sellers": sellers,
        "dim_geolocation": geolocation,}

    assert (silver["fact_order_items"]["price"] >= 0).all()
    assert (silver["fact_order_items"]["freight_value"] >= 0).all()
    assert (silver["fact_payments"]["payment_value"] >= 0).all()
    assert silver["fact_reviews"]["review_score"].between(1, 5).all()
    assert silver["fact_orders"]["customer_id"].isin(silver["dim_customers"]["customer_id"]).all()
    assert silver["fact_order_items"]["order_id"].isin(silver["fact_orders"]["order_id"]).all()
    assert silver["fact_order_items"]["product_id"].isin(silver["dim_products"]["product_id"]).all()
    assert silver["fact_order_items"]["seller_id"].isin(silver["dim_sellers"]["seller_id"]).all()

    return silver

def load_gold(silver, db_path="olist_warehouse.db", export_dir="gold_exports"):
    conn = sqlite3.connect(db_path)

    for table_name, df in silver.items():
        df_sql = df.copy()
        for col in df_sql.select_dtypes(include=["datetime64[ns]"]).columns:
            df_sql[col] = df_sql[col].dt.strftime("%Y-%m-%d %H:%M:%S")
        df_sql.to_sql(table_name, conn, if_exists="replace", index=False)

    gold_queries = {
        "gold_monthly_revenue": """
            SELECT
                SUBSTR(o.order_purchase_timestamp, 1, 7) AS order_month,
                COUNT(DISTINCT o.order_id) AS total_orders,
                ROUND(SUM(oi.total_item_value), 2) AS total_revenue_brl,
                ROUND(AVG(oi.total_item_value), 2) AS avg_item_value_brl
            FROM fact_orders o
            JOIN fact_order_items oi ON o.order_id = oi.order_id
            WHERE o.order_status = 'delivered'
            GROUP BY order_month
            ORDER BY order_month
        """,
        "gold_top_categories": """
            SELECT
                p.product_category_name_english AS category,
                COUNT(DISTINCT oi.order_id) AS total_orders,
                ROUND(SUM(oi.total_item_value), 2) AS total_revenue_brl
            FROM fact_order_items oi
            JOIN fact_orders o ON oi.order_id = o.order_id
            JOIN dim_products p ON oi.product_id = p.product_id
            WHERE o.order_status = 'delivered'
            GROUP BY p.product_category_name_english
            ORDER BY total_revenue_brl DESC
        """,
        "gold_delivery_reviews": """
            SELECT
                CASE WHEN o.is_late = 1 THEN 'Late' ELSE 'On Time' END AS delivery_status,
                COUNT(DISTINCT o.order_id) AS total_orders,
                ROUND(AVG(o.delivery_days), 2) AS avg_delivery_days,
                ROUND(AVG(r.review_score), 2) AS avg_review_score
            FROM fact_orders o
            JOIN fact_reviews r ON o.order_id = r.order_id
            WHERE o.order_status = 'delivered'
              AND o.delivery_days IS NOT NULL
            GROUP BY delivery_status
        """,
        "gold_customer_rfm": """
            WITH max_dt AS (
                SELECT MAX(order_purchase_timestamp) AS latest_date
                FROM fact_orders
                WHERE order_status = 'delivered'
            )
            SELECT
                c.customer_unique_id,
                CAST(JULIANDAY((SELECT latest_date FROM max_dt)) - JULIANDAY(MAX(o.order_purchase_timestamp)) AS INT) AS recency_days,
                COUNT(DISTINCT o.order_id) AS frequency,
                ROUND(SUM(oi.total_item_value), 2) AS monetary_brl
            FROM fact_orders o
            JOIN dim_customers c ON o.customer_id = c.customer_id
            JOIN fact_order_items oi ON o.order_id = oi.order_id
            WHERE o.order_status = 'delivered'
            GROUP BY c.customer_unique_id
        """,}
        
    Path(export_dir).mkdir(exist_ok=True)
    for table_name, query in gold_queries.items():
        conn.execute(f"DROP TABLE IF EXISTS {table_name};")
        conn.execute(f"CREATE TABLE {table_name} AS {query};")
        df_gold = pd.read_sql_query(f"SELECT * FROM {table_name};", conn)
        df_gold.to_csv(Path(export_dir) / f"{table_name}.csv", index=False)

    conn.close()

def main():
    data_dir = find_data_dir()
    bronze = extract_bronze(data_dir)
    silver = transform_silver(bronze)
    load_gold(silver)
    print("Pipeline completed: olist_warehouse.db and gold_exports/*.csv created!")

if __name__ == "__main__":
    main()
