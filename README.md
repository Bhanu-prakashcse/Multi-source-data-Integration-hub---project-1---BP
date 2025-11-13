# 🛍️ Multi-source Retail Data Integration Hub

## 📖 Project Overview
The **Multi-source Retail Data Integration Hub** is an end-to-end data engineering and analytics project designed to consolidate, clean, and analyze retail data from multiple sources — an **open retail transactions dataset** and a **product catalog API** — into a unified data warehouse.  

The system integrates **ETL pipelines**, implements **SCD Type 2** for tracking historical product changes, and visualizes key business metrics via an **interactive Streamlit dashboard** connected to **Google BigQuery**.

---

## 🎯 Objective
To build a complete **data integration and analytics solution** that:
- Combines data from multiple sources (CSV dataset + API).
- Performs cleaning, transformation, and dimensional modeling.
- Implements **Slowly Changing Dimension (SCD) Type 2** for historical tracking.
- Loads data into a **BigQuery data warehouse** using a 3-layer architecture.
- Visualizes insights through **Streamlit interactive dashboards**.

---

## 🏗️ Data Architecture
The project follows a standard **Medallion Architecture (Bronze → Silver → Gold)**.

### 🥉 Bronze Layer
- **Purpose:** Store raw data from multiple sources.
- **Sources Used:**
  - Retail Transactions Dataset (Kaggle)
  - Fake Store API (Product Catalog)
- **Process:**
  - Load CSV and JSON data into BigQuery as-is.
  - Minimal cleaning — preserves original schema.

### 🥈 Silver Layer
- **Purpose:** Clean and integrate data.
- **Transformations:**
  - Removed null or invalid entries.
  - Standardized columns and data types.
  - Joined **retail data (Bronze)** with **product catalog (API)** using product IDs.
- **Table Example:**
  - `Silver_layer-retail_enriched`
- **Output Columns:**
- Transaction_ID | Date | Customer_Name | Product | Total_Items | Total_Cost |
Payment_Method | City | Store_Type | Discount_Applied | Customer_Category | Season |
Promotion | product_id | product_name | category | product_price | rating


### 🥇 Gold Layer
- **Purpose:** Create dimensional and fact models for analytics.
- **Tables Created:**
- `dim_product` — Product details.
- `dim_customer` — Customer segmentation.
- `dim_date` — Calendar and seasonal data.
- `fact_sales` — Transaction-level metrics.
- **SCD Type 2 Table:**
- `dim_product_scd` tracks product version changes over time using:
  - `valid_from`, `valid_to`, and `is_current` columns.

---

## 🧠 SCD Type 2 Implementation
To maintain historical product price and description changes, **SCD Type 2** logic was applied on the product dimension:

```sql
MERGE `my_project_name.gold_layer.dim_product_scd` T
USING (
SELECT
  id AS product_id,
  title AS product_name,
  category,
  price AS product_price,
  description
FROM `my_project_name.bronze_layer.bronze_product_catalog`
WHERE title = "Mens Cotton Jacket"
) S
ON T.product_id = S.product_id AND T.is_current = TRUE
WHEN MATCHED THEN
UPDATE SET
  T.valid_to = CURRENT_TIMESTAMP(),
  T.is_current = FALSE;

INSERT INTO `my_project_name.gold_layer.dim_product_scd`
(product_id, product_name, category, product_price, product_description,
valid_from, valid_to, is_current)
VALUES (
3,
"Mens Cotton Jacket",
"men's clothing",
65.99,
"Updated version - new fabric quality for winter season",
CURRENT_TIMESTAMP(),
TIMESTAMP '9999-12-31 00:00:00',
TRUE
);

🧾 Result: The table now tracks multiple product versions with historical timestamps.

```
---

## 📊 Streamlit Dashboard
🔗 Live Connection

The dashboard connects directly to BigQuery Silver Layer using:
```sql
from google.cloud import bigquery
client = bigquery.Client(project="your_project_name")
query = "SELECT * FROM `my_project_name.dataset_name.Silver_layer-retail_enriched`"
df = client.query(query).to_dataframe()
```

---

## 📈 Key Performance Indicators (KPIs)

| Metric                  | Description                  |
| ----------------------- | ---------------------------- |
| 🧾 Total Transactions   | Number of sales transactions |
| 📦 Unique Products      | Distinct products sold       |
| 💰 Total Revenue        | Sum of total cost            |
| 🌆 Total Cities         | Unique store locations       |
| 👥 Total Customers      | Unique customer names        |
| 🏷️ Customer Categories | Distinct customer segments   |

---

## 📉 Visual Insights

| Visualization                   | Purpose                                  |
| ------------------------------- | ---------------------------------------- |
| 🏙️ Sales by City               | Compare revenue across cities            |
| 🏆 Top Products by Revenue      | Identify top-performing products         |
| 💳 Sales by Payment Method      | Analyze payment preferences              |
| 🏬 Sales by Store Type          | View store-type performance              |
| 👤 Revenue by Customer Category | Understand key demographics              |
| 📈 Seasonal Revenue Trend       | Observe sales pattern across seasons     |
| 💸 Discount Impact              | Compare discount vs non-discount revenue |

---

## 💡 Business Insights

Winter Season drives the highest sales volume.

Adults and Homemakers are the top customer categories.

Mobile payments are increasing in adoption.

Supermarkets and Department Stores show the highest revenue contribution.

Discount offers effectively improve average order revenue.

---

## 🧩 Tools and Technologies

| Category           | Tools                              |
| ------------------ | ---------------------------------- |
| Language           | Python                             |
| Data Storage       | Google BigQuery                    |
| Data Visualization | Streamlit, Plotly                  |
| API Integration    | Fake Store API                     |
| Data Source        | Kaggle Retail Transactions Dataset |
| Version Control    | Git, GitHub                        |

--- 

## 🚀 Deployment

🔹 Local Run: 
streamlit run data.py

---

## 👨‍💻 Developer

Dandu Bhanu Prakash
🎓 2025 Graduate (CSE-AIML)  || 
💼 Passionate about Data Engineering & Analytics ||
📫 GitHub Profile

---

## 🏁 Project Summary

This project successfully demonstrates:

End-to-end data engineering with multi-source integration.

BigQuery-based ETL architecture with data modeling.

Dimensional warehouse creation with historical tracking.

Real-time dashboard visualization using Streamlit.

---

## ⭐ If you liked this project, give it a star on GitHub!

git clone https://github.com/Bhanuprakash-cse16/Project-1---Multi-source-data-integration-hub---BP.git

## © 2025 Multi-source Retail Data Integration Hub | Developed by Dandu Bhanu Prakash

