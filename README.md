# E-Commerce Revenue, Logistics SLA & Retention Warehouse

Designed and built a **Medallion ELT pipeline (Bronze → Silver → Gold)** and **Star Schema data warehouse** analyzing **100,000+ marketplace orders** to diagnose revenue seasonality, last-mile delivery bottlenecks, and customer retention gaps

## Summary and Key Impact
- **Data Architecture:** Consolidated 9 raw relational tables (~1.4M records) into an 8-table **Star Schema** (`fact_orders`, `fact_order_items`, `fact_payments`, `fact_reviews`, `dim_customers`, `dim_products`, `dim_sellers`, `dim_geolocation`) in SQLite (`olist_warehouse.db`).
- **Automated Data Quality:** Removed out-of-bounds geolocation coordinates outside Brazil, deduplicated 261,831 exact geolocation rows, translated Portuguese product categories to English, and enforced foreign-key referential integrity checks.
- **Logistics & Customer Experience:** Quantified the impact of late deliveries on customer satisfaction, linking delivery SLA breaches directly to sharp drops in 1–5 star review scores.
- **Retention & RFM Insights:** Built SQL-driven **RFM (Recency, Frequency, Monetary)** customer segments, revealing that ~97% of buyers are one-time purchasers—pinpointing repeat-purchase retention as the primary growth lever.

## Pipeline Architecture
```text
9 Raw Source Tables (~1.4M rows)
        │
        ▼
[ Bronze Layer ]  Raw CSV ingestion + null & duplicate profiling
        │
        ▼
[ Silver Layer ]  Cleaning, English translation, geo-outlier removal & Star Schema
        │
        ▼
[  Gold Layer  ]  SQLite Warehouse (olist_warehouse.db) + Business Marts (CSV)
        │
        ▼
[  Analytics   ]  SQL KPIs, RFM Segmentation & Matplotlib Visuals
```

## Key Findings & Visuals

### 1. Monthly Revenue & Order Growth
<img width="3265" height="1320" alt="01_monthly_revenue" src="https://github.com/user-attachments/assets/c7254cc5-2541-428b-ba27-fbf9cc3db9da" />

### 2. Top Product Categories & Payment Mix
<img width="3870" height="1318" alt="02_categories_and_payments" src="https://github.com/user-attachments/assets/4bd58c7f-5adc-44cf-98c2-4b6dd88a1792" />

### 3. Delivery Performance vs. Customer Review Scores
<img width="2967" height="1170" alt="03_delivery_vs_reviews" src="https://github.com/user-attachments/assets/ba8ebc42-4f8c-4690-bb2e-d162f950dc12" />

### 4. Customer Retention & RFM Segmentation
<img width="2670" height="1168" alt="04_rfm_segments" src="https://github.com/user-attachments/assets/e63a4b4b-689f-4235-84d2-094bd365b4bf" />

## Business Recommendations
1. **Launch a Second-Order Loyalty Campaign:** With ~97% of buyers purchasing only once, target `Active / Promising` and `Recent High-Value` segments with time-bound post-delivery vouchers.
2. **Tighten Seller Delivery SLAs:** Flag sellers and regions driving late deliveries, as late orders cause steep drops in customer review scores.
3. **Capitalize on Quarter 4 Seasonality:** Align seller inventory and carrier capacity ahead of November Black Friday peaks.

## Repository Structure
- `pipeline.py` — Automated end-to-end Bronze → Silver → Gold Python ELT script
- `olist_elt_analytics.ipynb` — Interactive profiling, SQL queries, and visualizations
- `images/` — Exported analytical charts
- `requirements.txt` — Python dependencies
- `README.md` — Architecture, findings, and business recommendations

## How to Run
1. Download and unzip the [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) from Kaggle.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the automated ELT pipeline: `python pipeline.py`
4. Explore the analysis in `olist_elt_analytics.ipynb`.
