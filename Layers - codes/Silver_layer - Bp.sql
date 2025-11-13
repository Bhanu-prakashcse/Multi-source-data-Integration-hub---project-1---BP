CREATE OR REPLACE TABLE `sharedproject2025.Data_Integration_Hub_BP.Silver_layer-retail_enriched` AS
SELECT
  r.Transaction_ID,
  r.Date,
  r.Customer_Name,
  r.Product,
  r.Total_Items,
  r.Total_Cost,
  r.Payment_Method,
  r.City,
  r.Store_Type,
  r.Discount_Applied,
  r.Customer_Category,
  r.Season,
  r.Promotion,
  p.id AS product_id,
  p.title AS product_name,
  p.category,
  p.price AS product_price,
  p.description AS product_description,
  p.image AS product_image,
  p.rating
FROM
  `sharedproject2025.Data_Integration_Hub_BP.Bronze_layer-Retail_sales_BP` r
LEFT JOIN
  `sharedproject2025.Data_Integration_Hub_BP.bronze_product_catalog` p
ON
  LOWER(r.Product) = LOWER(p.title);
