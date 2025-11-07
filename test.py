from google.cloud import bigquery
client = bigquery.Client(project="trim-plexus-396409")
print("✅ Connected successfully!")


CREATE OR REPLACE TABLE `your_project.silver_layer.retail_enriched` AS
SELECT
  r.transaction_id,
  r.product_id,
  r.customer_id,
  r.quantity,
  r.total_amount,
  r.transaction_date,
  p.title AS product_name,
  p.category,
  p.price AS product_price,
  p.rating ->> '$.rate' AS rating,
  p.rating ->> '$.count' AS rating_count
FROM
  `your_project.bronze_layer.bronze_retail_data` r
LEFT JOIN
  `your_project.bronze_layer.bronze_product_catalog` p
ON
  CAST(r.product_id AS STRING) = CAST(p.id AS STRING);
