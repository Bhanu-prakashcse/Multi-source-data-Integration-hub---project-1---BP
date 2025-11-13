CREATE OR REPLACE TABLE `sharedproject2025.Data_Integration_Hub_BP.Gold_Layer-dim_customer` AS
SELECT
  DISTINCT
  r.Customer_Name AS customer_name,
  r.Customer_Category AS customer_category,
  r.City,
  r.Store_Type
FROM
  `sharedproject2025.Data_Integration_Hub_BP.Silver_layer-retail_enriched` r
WHERE
  r.Customer_Name IS NOT NULL;






CREATE OR REPLACE TABLE `sharedproject2025.Data_Integration_Hub_BP.Gold_Layer-dim_date` AS
SELECT
  DISTINCT
  DATE(r.Date) AS full_date,
  EXTRACT(YEAR FROM r.Date) AS year,
  EXTRACT(MONTH FROM r.Date) AS month,
  EXTRACT(DAY FROM r.Date) AS day,
  EXTRACT(DAYOFWEEK FROM r.Date) AS weekday,
  EXTRACT(QUARTER FROM r.Date) AS quarter,
  r.Season
FROM
  `sharedproject2025.Data_Integration_Hub_BP.Silver_layer-retail_enriched` r
WHERE
  r.Date IS NOT NULL;



CREATE OR REPLACE TABLE `sharedproject2025.Data_Integration_Hub_BP.Gold_Layer-dim_product` AS
SELECT DISTINCT
  Transaction_ID AS product_id,
  Product AS product_name,
  Customer_Category AS category,
  Total_Cost AS product_price,
  Promotion AS product_description,
  NULL AS product_image,   -- Placeholder for structure consistency
  4.0 AS rating            -- Temporary static rating (you can adjust later)
FROM
  `sharedproject2025.Data_Integration_Hub_BP.Silver_layer-retail_enriched`
WHERE
  Transaction_ID IS NOT NULL;







CREATE OR REPLACE TABLE `sharedproject2025.Data_Integration_Hub_BP.Gold_Layer-fact_sales` AS
SELECT
  r.Transaction_ID,
  DATE(r.Date) AS full_date,
  r.Customer_Name AS customer_name,
  p.product_id,
  r.Total_Items,
  r.Total_Cost,
  r.Payment_Method,
  r.Discount_Applied,
  r.Promotion
FROM
  `sharedproject2025.Data_Integration_Hub_BP.Silver_layer-retail_enriched` r
LEFT JOIN
  `sharedproject2025.Data_Integration_Hub_BP.Gold_Layer-dim_product` p
ON
  LOWER(r.Product) = LOWER(p.product_name);

