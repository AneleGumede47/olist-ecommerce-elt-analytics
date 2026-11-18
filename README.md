# Olist E-Commerce ELT Pipeline & Revenue Analytics

End-to-end **Data Engineering** and **Data Analytics** project built on **100,000+ real Brazilian e-commerce orders** across **9 relational CSV datasets** using **Python** (`pandas`, `matplotlib`) and **SQLite** (`sqlite3`).

## Architecture (Medallion: Bronze → Silver → Gold)
1. **Bronze Layer:** Ingested 9 raw Olist CSVs (~1.4M total rows) and ran automated null and duplicate profiling.
2. **Silver Layer:** Cleaned and modeled data into a **Star Schema** (`fact_orders`, `fact_order_items`, `fact_payments`, `fact_reviews`, `dim_customers`, `dim_products`, `dim_sellers`, `dim_geolocation`), translating Portuguese categories to English, removing Brazil geolocation outliers, deduplicating 261,831 exact geolocation rows, and verifying referential integrity.
3. **Gold Layer (`olist_warehouse.db`):** Loaded the Star Schema into SQLite and built 4 analytical Gold tables using SQL (`gold_monthly_revenue`, `gold_top_categories`, `gold_delivery_reviews`, `gold_customer_rfm`).

## Key Findings & Visuals

### 1. Monthly Revenue & Order Growth
<img width="3265" height="1320" alt="01_monthly_revenue" src="https://github.com/user-attachments/assets/c7254cc5-2541-428b-ba27-fbf9cc3db9da" />


### 2. Top Product Categories & Payment Mix
<img width="3870" height="1318" alt="02_categories_and_payments" src="https://github.com/user-attachments/assets/4bd58c7f-5adc-44cf-98c2-4b6dd88a1792" />


### 3. Delivery Performance vs. Customer Review Scores
<img width="2967" height="1170" alt="03_delivery_vs_reviews" src="https://github.com/user-attachments/assets/ba8ebc42-4f8c-4690-bb2e-d162f950dc12" />


### 4. Customer Retention & RFM Segmentation
<img width="2670" height="1168" alt="04_rfm_segments" src="https://github.com/user-attachments/assets/e63a4b4b-689f-4235-84d2-094bd365b4bf" />


## Dataset
- **Source:** [Brazilian E-Commerce Public Dataset by Olist (Kaggle)](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

## Repository Structure
- `olist_elt_analytics.ipynb` — Full Bronze → Silver → Gold ELT pipeline, SQL queries, and visualizations
- `images/` — Exported matplotlib charts
- `requirements.txt` — Python dependencies
- `README.md` — Project architecture and findings

## How to Run
1. Download and unzip the [Olist dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) from Kaggle.
2. Install dependencies: `pip install -r requirements.txt`
3. Update `DATA_DIR` in Cell 1 to your dataset folder and run `olist_elt_analytics.ipynb`.
