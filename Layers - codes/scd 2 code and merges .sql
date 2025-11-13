CREATE OR REPLACE TABLE `sharedproject2025.Data_Integration_Hub_BP.Gold_Layer-dim_product_scd` AS
SELECT
  p.product_id,
  p.product_name,
  p.category,
  p.product_price,
  p.product_description,
  CURRENT_TIMESTAMP() AS valid_from,
  TIMESTAMP('9999-12-31 00:00:00') AS valid_to,
  TRUE AS is_current
FROM `sharedproject2025.Data_Integration_Hub_BP.Gold_Layer-dim_product` p
WHERE p.product_id IS NOT NULL;



-- 1️⃣ Expire the current active record
UPDATE `sharedproject2025.Data_Integration_Hub_BP.Gold_Layer-dim_product_scd`
SET
  valid_to = CURRENT_TIMESTAMP(),
  is_current = FALSE
WHERE product_name = "Mens Cotton Jacket"
  AND is_current = TRUE;

-- 2️⃣ Insert a new version (new price or description)
INSERT INTO `sharedproject2025.Data_Integration_Hub_BP.Gold_Layer-dim_product_scd`
(
  product_id, product_name, category, product_price, product_description, valid_from, valid_to, is_current
)
VALUES (
  3,  -- same product_id
  "Mens Cotton Jacket",
  "men's clothing",
  65.99,  -- updated price
  "Updated version - new fabric quality for winter season",
  CURRENT_TIMESTAMP(),
  TIMESTAMP('9999-12-31 00:00:00'),
  TRUE
);


SELECT *
FROM `sharedproject2025.Data_Integration_Hub_BP.Gold_Layer-dim_product_scd`
WHERE product_name = "Mens Cotton Jacket"
ORDER BY valid_from DESC;



INSERT INTO `sharedproject2025.Data_Integration_Hub_BP.Gold_Layer-dim_product_scd`
(
  product_id, product_name, category, product_price, product_description,
  valid_from, valid_to, is_current
)
VALUES (
  3,  -- same product_id
  "Mens Cotton Jacket",
  "men's clothing",
  56.99,
  "Updated version - new fabric quality for winter season",
  CURRENT_TIMESTAMP(),
  TIMESTAMP('9999-12-31 00:00:00'),
  TRUE
);

UPDATE `sharedproject2025.Data_Integration_Hub_BP.Gold_Layer-dim_product_scd`
SET
  valid_to = CURRENT_TIMESTAMP(),
  is_current = FALSE
WHERE product_name = "Mens Cotton Jacket"
  AND is_current = TRUE;


SELECT *
FROM `sharedproject2025.Data_Integration_Hub_BP.Gold_Layer-dim_product_scd`
WHERE product_name = "Mens Cotton Jacket"
ORDER BY valid_from DESC;


INSERT INTO `sharedproject2025.Data_Integration_Hub_BP.Gold_Layer-dim_product_scd`
VALUES (
  3,
  "Mens Cotton Jacket",
  "men's clothing",
  55.99,
  "Original product description",
  TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 5 DAY),
  TIMESTAMP('9999-12-31 00:00:00'),
  TRUE
);



DELETE FROM `sharedproject2025.Data_Integration_Hub_BP.Gold_Layer-dim_product_scd`
WHERE product_price = 56.99
  AND is_current = FALSE;
















UPDATE `sharedproject2025.Data_Integration_Hub_BP.Gold_Layer-dim_product_scd`
SET
  valid_to = CURRENT_TIMESTAMP(),
  is_current = FALSE
WHERE product_name = "Lock and Love Women's Removable Hooded Faux Leather Moto Biker Jacket"
  AND is_current = TRUE;


